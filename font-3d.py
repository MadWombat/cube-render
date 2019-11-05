from pathlib import Path

import numpy as np
import tensorflow as tf

from PIL import Image, ImageDraw, ImageFont


def render2d(txt, ttf_file, size, pad=0):
    if not Path(ttf_file).exists():
        raise ValueError("font file %s doesn't exist" % ttf_file)
    font = ImageFont.truetype(ttf_file, size=size - pad)
    text = Image.new('1', font.getsize(txt), 0)  # black by default
    draw = ImageDraw.Draw(text)
    draw.text((0, 0), txt, fill=1, font=font)
    text = text.crop(text.getbbox())
    image = Image.new('1', (size, size), 0)
    tw, th = text.size
    pos_x = (size - tw) // 2
    pos_y = (size - th) // 2
    image.paste(text, (pos_x, pos_y))
    return image


def create_model(size):
    return tf.keras.models.Sequential([
        tf.keras.layers.InputLayer(input_shape=(1, )),
        tf.keras.layers.Dense(256, activation='relu'),
        tf.keras.layers.Dense(256, activation='relu'),
        tf.keras.layers.Dense(256, activation='relu'),
        tf.keras.layers.Dense(256, activation='relu'),
        tf.keras.layers.Dense(size ** 3),
        tf.keras.layers.Reshape([size, size, size])
    ])

@tf.function
def loss(y_true, y_pred):
    """
    y_true is of shape [3, size, size] with three expected views of the cube
    y_pred is of shape [size, size, size], the cube generated by the model
    """
    x = tf.losses.kld(y_true[0], tf.reduce_sum(y_pred, axis=0))
    y = tf.losses.kld(y_true[1], tf.reduce_sum(y_pred, axis=1))
    z = tf.losses.kld(y_true[2], tf.reduce_sum(y_pred, axis=2))
    return x + y + z


if __name__ == '__main__':
    symb = 'A'
    size = 128
    ttf = '/Library/Fonts/Comic Sans MS.ttf'
    img = render2d(symb, ttf, size)
    data = np.array(img.getdata())
    data = data.reshape([size, size])
    model = create_model(size)
    model.compile
