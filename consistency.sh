#bash
# execute chmod 777 consistency.sh to make it executable (only once)
# then call it for example: ./consistency.sh en-fr-200k en fr
# so this is ./consistency [pipeline] [src_lang] [tgt_lang] (edited) 
# sample error response:
#   en-fr-200k: error
#   aligned: 0
#   parsed_src: 184025
#   parsed_tgt: 184025
#   tokenized_src: 184025
#   tokenized_tgt: 184025
# sample ok response:
#   en-fr-200k: ok
#   sentences: 184025
# it works always on _* files (edited) 
# it can take a minute for large files

pipeline=$1

# Set - as the delimiter
IFS='-'

#Read the split words into an array based on space delimiter
read -a strarr <<< "$PIPELINE"

echo "source : ${strarr[0]}"
echo "target : ${strarr[1]}"

src="${strarr[0]}"
tgt="${strarr[1]}"

file_aligned=./data/$pipeline/aligned/_training.align
file_parsed_src=./data/$pipeline/parsed/_$pipeline.$src.parsed.conllu
file_parsed_tgt=./data/$pipeline/parsed/_$pipeline.$tgt.parsed.conllu
file_tokenized_src=./data/$pipeline/tokenized/_$pipeline.$src.tokenized.txt
file_tokenized_tgt=./data/$pipeline/tokenized/_$pipeline.$tgt.tokenized.txt

aligned_len=$(grep -iF "" $file_aligned | wc -l);
parsed_src_len=$(grep -iF "sent_id" $file_parsed_src | wc -l);
parsed_tgt_len=$(grep -iF "sent_id" $file_parsed_tgt | wc -l);
tokenized_src_len=$(grep -iF "" $file_tokenized_src | wc -l);
tokenized_tgt_len=$(grep -iF "" $file_tokenized_tgt | wc -l);

if (( $aligned_len == $parsed_src_len && $aligned_len == $parsed_tgt_len && $aligned_len == $tokenized_src_len && $aligned_len == $tokenized_tgt_len )); then
    echo $pipeline": ok"
    echo "sentences:"$aligned_len
else
    echo $pipeline": error"
    echo "aligned:"$aligned_len
    echo "parsed_src:"$parsed_src_len
    echo "parsed_tgt:"$parsed_tgt_len
    echo "tokenized_src:"$tokenized_src_len
    echo "tokenized_tgt:"$tokenized_tgt_len
fi