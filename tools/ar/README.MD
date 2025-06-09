# 阿拉伯语 F5-TTS 训练数据预处理

## 添加元音符号

- 元音恢复模型：[catt](git@github.com:abjadai/catt.git)

## 添加标点符号

- 标点符号模型：[1-800-BAD-CODE/xlm-roberta_punctuation_fullstop_truecase](https://huggingface.co/1-800-BAD-CODE/xlm-roberta_punctuation_fullstop_truecase)
  调用方式：

  ```python
    # pip install punctuators
    from typing import List
    from punctuators.models import PunctCapSegModelONNX
    m: PunctCapSegModelONNX = PunctCapSegModelONNX.from_pretrained(
        "1-800-BAD-CODE/xlm-roberta_punctuation_fullstop_truecase"
    )
    input_texts: List[str] = [
        "hola mundo cómo estás estamos bajo el sol y hace mucho calor santa coloma abre los huertos urbanos a las escuelas de la ciudad",
        "hello friend how's it going it's snowing outside right now in connecticut a large storm is moving in",
        "未來疫苗將有望覆蓋3歲以上全年齡段美國與北約軍隊已全部撤離還有鐵路公路在內的各項基建的來源都將枯竭",
        "በባለፈው ሳምንት ኢትዮጵያ ከሶማሊያ 3 ሺህ ወታደሮቿንም እንዳስወጣች የሶማሊያው ዳልሳን ሬድዮ ዘግቦ ነበር ጸጥታ ሃይሉና ህዝቡ ተቀናጅቶ በመስራቱ በመዲናዋ ላይ የታቀደው የጥፋት ሴራ ከሽፏል",
        "こんにちは友人" "調子はどう" "今日は雨の日でしたね" "乾いた状態を保つために一日中室内で過ごしました",
        "hallo freund wie geht's es war heute ein regnerischer tag nicht wahr ich verbrachte den tag drinnen um trocken zu bleiben",
        "हैलो दोस्त ये कैसा चल रहा है आज बारिश का दिन था न मैंने सूखा रहने के लिए दिन घर के अंदर बिताया",
        "كيف تجري الامور كان يومًا ممطرًا اليوم أليس كذلك قضيت اليوم في الداخل لأظل جافًا",
    ]

    results: List[List[str]] = m.infer(
        texts=input_texts, apply_sbd=True,
    )
    for input_text, output_texts in zip(input_texts, results):
        print(f"Input: {input_text}")
        print(f"Outputs:")
        for text in output_texts:
            print(f"\t{text}")
        print()
  ```

  - 小时数：1569.69