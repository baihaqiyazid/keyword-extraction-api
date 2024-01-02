#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu May 19 13:08:49 2022

@author: putri
"""
import numpy as np
from app.data.helper.cleaning import stopwordsid2, prefinkb
from sklearn.feature_extraction.text import CountVectorizer
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import itertools

model = SentenceTransformer('distiluse-base-multilingual-cased-v2')

# Extract candidate words/phrases
def extract_candidate(doc, n_gram_range):
    count = CountVectorizer(ngram_range=n_gram_range, stop_words=stopwordsid2).fit([doc])
    candidates = count.get_feature_names_out()
    return candidates

def doc_emb(doc):
    doc_embedding = model.encode([doc])
    return doc_embedding

def cand_emb(candidates):
    candidate_embeddings = model.encode(candidates)
    return candidate_embeddings

def keybertid(doc, n_gram_range, top_n):
    clean_text = prefinkb(doc)
    candidates = extract_candidate(clean_text, n_gram_range)
    doc_embedding = doc_emb(doc)
    candidate_embeddings = cand_emb(candidates)
    top_n = top_n
    distances = cosine_similarity(doc_embedding, candidate_embeddings)
    keywords = [candidates[index] for index in distances.argsort()[0][-top_n:]]
    return keywords

def max_sum_sim(doc, n_gram_range, top_n, nr_candidates):
    # Calculate distances and extract keywords
    clean_text = prefinkb(doc)
    candidates = extract_candidate(clean_text, n_gram_range)
    candidate_embeddings = cand_emb(candidates)
    doc_embedding = doc_emb(doc)

    distances = cosine_similarity(doc_embedding, candidate_embeddings)
    distances_candidates = cosine_similarity(candidate_embeddings, 
                                            candidate_embeddings)

    # Get top_n words as candidates based on cosine similarity
    words_idx = list(distances.argsort()[0][-nr_candidates:])
    words_vals = [candidates[index] for index in words_idx]
    distances_candidates = distances_candidates[np.ix_(words_idx, words_idx)]

    # Calculate the combination of words that are the least similar to each other
    min_sim = np.inf
    candidate = None
    for combination in itertools.combinations(range(len(words_idx)), top_n):
        sim = sum([distances_candidates[i][j] for i in combination for j in combination if i != j])
        if sim < min_sim:
            candidate = combination
            min_sim = sim

    return [words_vals[idx] for idx in candidate]

def mmr(doc, n_gram_range, top_n, diversity):
    clean_text = prefinkb(doc)
    candidates = extract_candidate(clean_text, n_gram_range)
    candidate_embeddings = cand_emb(candidates)
    doc_embedding = doc_emb(doc)

    # Extract similarity within words, and between words and the document
    word_doc_similarity = cosine_similarity(candidate_embeddings, doc_embedding)
    word_similarity = cosine_similarity(candidate_embeddings)

    # Initialize candidates and already choose best keyword/keyphras
    keywords_idx = [np.argmax(word_doc_similarity)]
    candidates_idx = [i for i in range(len(candidates)) if i != keywords_idx[0]]

    for _ in range(top_n - 1):
        # Extract similarities within candidates and
        # between candidates and selected keywords/phrases
        candidate_similarities = word_doc_similarity[candidates_idx, :]
        target_similarities = np.max(word_similarity[candidates_idx][:, keywords_idx], axis=1)

        # Calculate MMR
        mmr = (1-diversity) * candidate_similarities - diversity * target_similarities.reshape(-1, 1)
        mmr_idx = candidates_idx[np.argmax(mmr)]

        # Update keywords & candidates
        keywords_idx.append(mmr_idx)
        candidates_idx.remove(mmr_idx)

    return [candidates[idx] for idx in keywords_idx]