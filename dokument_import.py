def dokument_import():
    # Pfad zum Bild
    image_path = input("Pfad zum Bild eingeben: ")

    # ======================
    # EASY OCR
    # ======================
    try:
        from easyocr import Reader
        reader = Reader(['de'], gpu=False)
        easy_results = reader.readtext(image_path, detail=0)
        easy_text = "\n".join(easy_results)
        print("=== EASY OCR ===")
        print(easy_text)
        print()
    except Exception as e:
        print("EasyOCR konnte nicht geladen werden:", e)
        print()

    # ======================
    # PADDLE OCR
    # ======================
    try:
        from paddleocr import PaddleOCR
        ocr = PaddleOCR(
            lang='german',
            use_angle_cls=False,
            use_gpu=False,
            show_log=False
        )

        paddle_result = ocr.ocr(image_path, cls=False)
        paddle_text_lines = []
        for line in paddle_result:
            for _, (text, score) in line:
                paddle_text_lines.append(text)

        paddle_text = "\n".join(paddle_text_lines)

        print("=== PADDLE OCR ===")
        print(paddle_text)
    except Exception as e:
        print("PaddleOCR konnte nicht geladen werden:", e)
        print()
