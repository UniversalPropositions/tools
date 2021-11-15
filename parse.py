import stanza
import time

stanza.download('en')

nlp = stanza.Pipeline('en', processors='tokenize,pos,lemma,depparse', use_gpu=True, pos_batch_size=3000) # Build the pipeline, specify part-of-speech processor's batch size

text = 'What if Google expanded on its search-engine (and now e-mail) wares into a full-fledged operating system?'
documents = []
for i in range(0,10000):
    documents.append(text)
in_docs = [stanza.Document([], text=d) for d in documents] # Wrap each document with a stanza.Document object
s1 = time.time()
out_docs = nlp(in_docs) # Call the neural pipeline on this list of documents
s2 = time.time()
print(out_docs[0])
print(f'processing time: {s2-s1} seconds')