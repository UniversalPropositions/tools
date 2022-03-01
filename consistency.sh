#bash
src=$1
tgt=$2
pipeline=$src-$tgt
file_aligned=./data/$pipeline/aligned/_training.align
file_parsed_src=./data/$pipeline/parsed/_$src-$tgt.$src.parsed.conllu
file_parsed_tgt=./data/$pipeline/parsed/_$src-$tgt.$tgt.parsed.conllu
file_tokenized_src=./data/$pipeline/tokenized/_$src-$tgt.$src.tokenized.txt
file_tokenized_tgt=./data/$pipeline/tokenized/_$src-$tgt.$tgt.tokenized.txt

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