from datetime import datetime
from io import BytesIO
import logging
from pathlib import Path

import cv2
from image_similarity_measures.quality_metrics import psnr
import numpy as np
from telegram.ext import (
    # DictPersistence,
    CommandHandler,
    ConversationHandler,
    Filters,
    MessageHandler,
    Updater,
)
from telegram.ext.dispatcher import run_async

from db import Session, User, Picture
from config import TOKEN, PSNR_THRESHOLD, IMAGE_DIR


logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)


def create_or_update_user(telegram_id):
    session = Session()

    user = session.query(User).filter_by(telegram_id=telegram_id).first()
    if not user:
        user = User(telegram_id=telegram_id)
        session.add(user)
        session.commit()

    session.close()

    return user


def save_picture(image_buf, save_path, message_link):
    session = Session()

    new_pic = Picture(path=str(save_path), message_link=message_link)
    session.add(new_pic)

    with open(save_path, "wb") as save_f:
        save_f.write(image_buf)

    session.commit()
    session.close()


def find_similar(image_buf, image_size, save_path, message_link):
    img_array = np.frombuffer(image_buf, dtype=np.uint8)
    new_img = cv2.imdecode(img_array, cv2.IMREAD_COLOR)

    session = Session()
    pictures = session.query(Picture).all()
    session.close()

    start_time = datetime.now()
    logging.info(f"Checking {len(pictures)} images for similarities")

    for p in pictures:
        old_image = cv2.imread(p.path)
        old_image = cv2.resize(old_image, image_size)
        psnr_score = psnr(new_img, old_image)
        # logging.info(f"{old_image_path.name}: psnr {psnr_score}")
        if psnr_score > PSNR_TRESHOLD:
            psnr_score = psnr_score if not np.isinf(psnr_score) else 100
            return psnr_score, p.message_link

    save_picture(image_buf, save_path, message_link)
    logging.info(f"Checked {len(pictures)} images in {datetime.now() - start_time}")


def start(update, context):
    chat_id = update.effective_chat.id
    logging.info(f"{chat_id} started")
    update.effective_chat.send_message(
        text="Привет! Отправь мне картинку и я проверю, постили ее или нет"
    )


def check_image(update, context):
    chat_id = update.effective_chat.id
    create_or_update_user(chat_id)

    message_link = update.message.link

    photo = update.message.photo[0]
    image_size = photo.width, photo.height
    image_file = photo.get_file()
    image_buf = image_file.download_as_bytearray()

    save_path = IMAGE_DIR / f"{photo.file_id}.jpg"

    similar = find_similar(image_buf, image_size, save_path, message_link)
    if similar:
        score, link = similar
        update.message.reply_text(
            f"Мы на {int(score)}% уверены, что это уже было {link or ''}",
            disable_web_page_preview=True,
        )


def error_callback(update, context):
    logging.error(context.error)


updater = Updater(
    token=TOKEN,
    use_context=True,
    # persistence=DictPersistence
)
dispatcher = updater.dispatcher

start_handler = CommandHandler('start', start)
image_handler = MessageHandler(Filters.photo, check_image)

dispatcher.add_handler(start_handler)
dispatcher.add_handler(image_handler)
# dispatcher.add_error_handler(error_callback)

updater.start_polling()
