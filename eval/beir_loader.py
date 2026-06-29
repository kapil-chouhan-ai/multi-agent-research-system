"""
Loads BEIR-format datasets (corpus.jsonl / queries.jsonl / qrels/{split}.tsv).
Format and download URL verified against github.com/beir-cellar/beir
(beir/datasets/data_loader.py, beir/util.py) rather than guessed.

corpus.jsonl line:  {"_id": "...", "title": "...", "text": "..."}
queries.jsonl line: {"_id": "...", "text": "..."}
qrels/test.tsv:     header row, then  query-id \t corpus-id \t score
"""
import csv
import json
import os
import random
import zipfile

import requests

UKP_BASE_URL = "https://public.ukp.informatik.tu-darmstadt.de/thakur/BEIR/datasets/{name}.zip"


def download_and_unzip(name: str, datasets_dir: str) -> str:
    """Downloads {name}.zip from the official BEIR host and unzips it into
    datasets_dir. Needs network access to public.ukp.informatik.tu-darmstadt.de
    -- if that's blocked in your environment, download the zip manually and
    extract it to datasets_dir/{name}/ instead, then call load_beir_dataset
    with download_if_missing=False.
    """
    os.makedirs(datasets_dir, exist_ok=True)
    zip_path = os.path.join(datasets_dir, f"{name}.zip")
    target_dir = os.path.join(datasets_dir, name)

    if os.path.exists(target_dir):
        return target_dir

    url = UKP_BASE_URL.format(name=name)
    print(f"Downloading {url} ...")
    response = requests.get(url, stream=True, timeout=120)
    response.raise_for_status()
    with open(zip_path, "wb") as f:
        for chunk in response.iter_content(chunk_size=8192):
            f.write(chunk)

    print(f"Unzipping {name}.zip ...")
    with zipfile.ZipFile(zip_path) as zf:
        zf.extractall(datasets_dir)
    os.remove(zip_path)

    return target_dir


def _load_corpus(corpus_path: str) -> dict[str, dict[str, str]]:
    corpus = {}
    with open(corpus_path, encoding="utf8") as f:
        for line in f:
            row = json.loads(line)
            corpus[row["_id"]] = {"title": row.get("title", ""), "text": row.get("text", "")}
    return corpus


def _load_queries(query_path: str) -> dict[str, str]:
    queries = {}
    with open(query_path, encoding="utf8") as f:
        for line in f:
            row = json.loads(line)
            queries[row["_id"]] = row["text"]
    return queries


def _load_qrels(qrels_path: str) -> dict[str, dict[str, int]]:
    qrels: dict[str, dict[str, int]] = {}
    with open(qrels_path, encoding="utf8") as f:
        reader = csv.reader(f, delimiter="\t", quoting=csv.QUOTE_MINIMAL)
        next(reader)  # header: query-id, corpus-id, score
        for row in reader:
            qid, docid, score = row[0], row[1], int(row[2])
            qrels.setdefault(qid, {})[docid] = score
    return qrels


def load_beir_dataset(
    name: str,
    datasets_dir: str,
    split: str = "test",
    download_if_missing: bool = True,
):
    """Returns (corpus, queries, qrels):
      corpus:  {doc_id: {"title": str, "text": str}}
      queries: {query_id: str}            -- filtered to only those with qrels
      qrels:   {query_id: {doc_id: relevance_int}}
    """
    data_dir = os.path.join(datasets_dir, name)
    if not os.path.exists(data_dir):
        if not download_if_missing:
            raise FileNotFoundError(
                f"{data_dir} not found and download_if_missing=False. "
                f"Download {name}.zip from {UKP_BASE_URL.format(name=name)} "
                f"and extract it to {data_dir}/ yourself."
            )
        data_dir = download_and_unzip(name, datasets_dir)

    corpus = _load_corpus(os.path.join(data_dir, "corpus.jsonl"))
    queries = _load_queries(os.path.join(data_dir, "queries.jsonl"))
    qrels = _load_qrels(os.path.join(data_dir, "qrels", f"{split}.tsv"))

    queries = {qid: text for qid, text in queries.items() if qid in qrels}

    return corpus, queries, qrels


def sample_queries(queries: dict[str, str], qrels: dict[str, dict[str, int]], n: int, seed: int = 42):
    """Subsamples down to n queries (or fewer if the dataset has fewer),
    deterministically. Corpus is left untouched -- BEIR's protocol retrieves
    against the FULL corpus regardless of how many queries you evaluate;
    sampling queries (not documents) is what keeps eval cost down without
    changing what's actually being measured.
    """
    qids = sorted(queries.keys())
    if n >= len(qids):
        return queries, qrels
    rng = random.Random(seed)
    sampled = set(rng.sample(qids, n))
    return (
        {qid: queries[qid] for qid in sampled},
        {qid: qrels[qid] for qid in sampled},
    )