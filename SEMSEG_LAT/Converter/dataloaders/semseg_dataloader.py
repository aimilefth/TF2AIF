import tensorflow as tf
import os

def preprocess(image):
    NORM_FACTOR = 127.5
    image = tf.cast(image, dtype=tf.float32)
    image = image / NORM_FACTOR - 1.0
    return image

def get_dataloader(dataset_path_name, batch_size, quantization_samples):
    """
    This function should have this exact name and arguments. It is used for quantization to INT8.
    It should return a tf.data.Dataset object with the given batch_size and quantization_samples number of elements.
    Using tf.data.Dataset.repeat() is best to ensure enough samples.
    The dataset should not contain labels, only input data.
    The datasets sources should exist on the datasets directory.
    """
    ds_quant = tf.keras.preprocessing.image_dataset_from_directory(
            directory = dataset_path_name,
            labels = 'inferred',
            label_mode = None,
            color_mode = "rgb",
            batch_size = batch_size,
            image_size = (224,224),
            shuffle = False
    )
    ds_quant = ds_quant.unbatch().batch(batch_size, drop_remainder=True) # Force drop remainder
    ds_quant = ds_quant.map(lambda x: preprocess(x))
    return ds_quant.repeat().take(quantization_samples)