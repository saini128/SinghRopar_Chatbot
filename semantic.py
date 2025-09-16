import os
from datetime import datetime
import config
from sentence_transformers import SentenceTransformer
import annoy

from db.init import SessionLocal
from models.chat_models import ChatLog
from models.config_models import AnnoyIndexDB

# Globals
model = None
annoy_index = None
queue_val = 0
pending_embeddings = []  # buffer for (embedding, sentence)


def init():
    global model, annoy_index
    model = SentenceTransformer(config.EMBEDDING_MODEL, device="cpu")
    embedding_dim = model.get_sentence_embedding_dimension()
    annoy_index = annoy.AnnoyIndex(embedding_dim, 'angular')

    if os.path.exists(config.ANNOY_DB):
        annoy_index.load(config.ANNOY_DB)
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Loaded existing Annoy index.")
    else:
        annoy_index.build(config.ANNOY_TREES)
        annoy_index.save(config.ANNOY_DB)
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Created new Annoy index.")


def create_embedding(text: str):
    return model.encode(text)


def find_similar_answer(query_embedding) -> str | None:
    n_neighbors = 1
    item_ids, distances = annoy_index.get_nns_by_vector(
        query_embedding, n_neighbors, include_distances=True
    )

    if distances:  # check before accessing
        print(f"Found similar embedding with distance {distances[0]:.4f}")
        if distances[0] < config.SEMANTIC_THRESHOLD:
            ques = id_to_index(item_ids[0])
            return answer_to_ques(ques)
    else:
        print("No embeddings found in Annoy index.")

    return None



def rebuild_cache(new_embedding, sentence: str):
    global queue_val, pending_embeddings, annoy_index

    # Store in memory
    pending_embeddings.append((new_embedding, sentence))
    queue_val += 1

    if queue_val < config.ANNOY_BUFFER:
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Buffering embedding {queue_val}/{config.ANNOY_BUFFER}...")
        return

    queue_val = 0
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Rebuilding Annoy index with {len(pending_embeddings)} new embeddings...")

    db = SessionLocal()
    try:
        # Save pending embeddings into DB
        for emb, sent in pending_embeddings:
            new_id = db.query(AnnoyIndexDB).count()  # sequential ID
            db.add(AnnoyIndexDB(id=new_id, sentence=sent))

            # Also save full ChatLog reference
            db.add(ChatLog(
                user_message=sent,
                bot_response="",  # will be filled later
                api_hit=False,
                timestamp=datetime.now().isoformat(),
                prompt_tokens=0,
                completion_tokens=0,
                total_time=0,
                success=True
            ))
        db.commit()
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Saved {len(pending_embeddings)} new embeddings to DB.")

        # 🔑 Rebuild fresh Annoy index from DB
        embedding_dim = model.get_sentence_embedding_dimension()
        new_index = annoy.AnnoyIndex(embedding_dim, 'angular')

        all_entries = db.query(AnnoyIndexDB).all()
        for entry in all_entries:
            emb = model.encode(entry.sentence)
            new_index.add_item(entry.id, emb)

        new_index.build(config.ANNOY_TREES)
        new_index.save(config.ANNOY_DB)
        annoy_index = new_index  # swap in new index
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Saved updated Annoy index with {len(all_entries)} items.")
    finally:
        db.close()

    # Clear buffer
    pending_embeddings = []


def id_to_index(id: int) -> str | None:
    db = SessionLocal()
    try:
        annoy_entry = db.query(AnnoyIndexDB).filter(AnnoyIndexDB.id == id).first()
        if annoy_entry:
            return annoy_entry.sentence
    finally:
        db.close()
    return None

def answer_to_ques(ques:str) -> ChatLog| None:
    db=SessionLocal()
    try:
        ans=db.query(ChatLog).filter(ChatLog.user_message==ques, ChatLog.api_hit==True, ChatLog.success==True).first()
        if ans:
            return ans
    finally:
        db.close()
    return None