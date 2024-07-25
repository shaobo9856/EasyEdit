import json
import os
from googletrans import Translator
from nltk.translate.bleu_score import sentence_bleu, SmoothingFunction
import nltk
import deepl
import time
# 下载punkt用于tokenize
nltk.download('punkt')

# 设置文件夹路径
folder_path = './data/WikiFactDiff/' # MCounterFact  MzsRE  WikiFactDiff 

auth_key = "4d7cbf44-8015-4de4-868d-0f9b4668f17c:fx"  # Replace with your key
translator = deepl.Translator(auth_key)

# translator = Translator()
# translator.raise_Exception = True

def translate_text(text, src_lang, dest_lang='EN-US'):
    try:
        time.sleep(0.1)
        # translation = translator.translate(text, src=src_lang, dest=dest_lang)
        translation = translator.translate_text(text, target_lang=dest_lang)
        print(translation.text)
        return translation.text
    except Exception as e:
        print(f"Translation error: {e}")
        return ""

def compute_bleu_score(reference, hypothesis, n_gram=1):
    reference_tokens = nltk.word_tokenize(reference)
    hypothesis_tokens = nltk.word_tokenize(hypothesis)

    weights = [1.0 / n_gram] * n_gram
    smoothing_function = SmoothingFunction().method1
    return sentence_bleu([reference_tokens], hypothesis_tokens, weights=weights, smoothing_function=smoothing_function) #

# 遍历文件夹中的所有JSON文件
all_results = []
lang_list = ["es", "vi", "ru", "zh-cn", "de" ] #'af', 'ar', 'az', 'be', 'bg', 'bn', 'ca', 'cs', 'cy', 'da', 'de', 'eb', 'el', 'en', 'es', 'es', 'et', 'eu', 'fa', 'fi', 'fr', 'ga', 'gl', 'he', 'hi', 'hr', 'hu', 'hy', 'id', 'it', 'ja', 'ka', 'ko', 'la', 'lt', 'lv', 'ms', 'nl', 'pl', 'pt', 'ro', 'ru', 'sk', 'sl', 'sq', 'sr', 'sv', 'ta', 'th', 'tr', 'uk', 'ur', 'vi']
for filename in os.listdir(folder_path):
    if 'wfd_test_' in filename and not 'enen' in filename:   # mcounterfact_test_   mzsre_test_duplicate_    wfd_test_
        # lang2_code = filename.split('_')[-1].split('.')[0]
        # all_results.append(lang2_code[-2:])
        # print(sorted(all_results))
        # continue
        file_path = os.path.join(folder_path, filename)
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        results = []
        print(filename)
        print(data[0].keys())
        lang2_code = list(data[0].keys())[1]
        if not lang2_code in lang_list: 
                print(f"error code: {lang2_code}") 
                continue
    
        for item in data[:50]: # 
            en_texts = item['en']
            # lang2_code = list(item.keys())[1]  # 获取非英语语言代码
            lang2_texts = item[lang2_code]

            # 翻译所有非英语文本
            translated_src = translate_text(lang2_texts['src'], src_lang=lang2_code)
            translated_rephrase = translate_text(lang2_texts['rephrase'], src_lang=lang2_code)
            translated_alt = translate_text(lang2_texts['alt'], src_lang=lang2_code)
            translated_loc = translate_text(lang2_texts['loc'], src_lang=lang2_code)
            translated_loc_ans = translate_text(lang2_texts['loc_ans'], src_lang=lang2_code)
            translated_new_question = translate_text(lang2_texts['portability']['New Question'], src_lang=lang2_code)
            translated_new_answer = translate_text(lang2_texts['portability']['New Answer'], src_lang=lang2_code)

            # 计算BLEU分数
            bleu_scores = {
                'src': compute_bleu_score(en_texts['src'], translated_src),
                'rephrase': compute_bleu_score(en_texts['rephrase'], translated_rephrase),
                'alt': compute_bleu_score(en_texts['alt'], translated_alt),
                'loc': compute_bleu_score(en_texts['loc'], translated_loc),
                'loc_ans': compute_bleu_score(en_texts['loc_ans'], translated_loc_ans),
                'new_question': compute_bleu_score(en_texts['portability']['New Question'], translated_new_question),
                'new_answer': compute_bleu_score(en_texts['portability']['New Answer'], translated_new_answer)
            }

            avg_bleu_score = sum(bleu_scores.values()) / len(bleu_scores)

            results.append({
                'original_texts': lang2_texts,
                'translated_texts': {
                    'src': translated_src,
                    'rephrase': translated_rephrase,
                    'alt': translated_alt,
                    'loc': translated_loc,
                    'loc_ans': translated_loc_ans,
                    'new_question': translated_new_question,
                    'new_answer': translated_new_answer
                },
                'en_texts': {
                    'src': en_texts['src'],
                    'rephrase': en_texts['rephrase'],
                    'alt': en_texts['alt'],
                    'loc': en_texts['loc'],
                    'loc_ans': en_texts['loc_ans'],
                    'new_question': en_texts['portability']['New Question'],
                    'new_answer': en_texts['portability']['New Answer']
                }, 
                'bleu_scores': bleu_scores,
                'avg_bleu_score': avg_bleu_score
            })
            print(results[-1])
        
        # 保存结果到文件
        output_filename = f'result/{os.path.splitext(filename)[0]}_translation_bleu_scores.json'
        output_filepath = os.path.join(folder_path, output_filename)
        with open(output_filepath, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=4)

        # 计算每个文件的平均BLEU分数
        file_avg_bleu_score = sum(result['avg_bleu_score'] for result in results) / len(results)
        all_results.append({
            'filename': filename,
            'file_avg_bleu_score': file_avg_bleu_score
        })
        print(f"Processed {filename}, File Average BLEU Score: {file_avg_bleu_score}")

# 保存所有文件的平均BLEU分数到汇总文件
with open(os.path.join(folder_path, 'result/all_files_avg_bleu_scores.json'), 'w', encoding='utf-8') as f:
    json.dump(all_results, f, ensure_ascii=False, indent=4)

for result in all_results:
    print(f"Filename: {result['filename']}, Average BLEU Score: {result['file_avg_bleu_score']}")
