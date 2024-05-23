import tensorflow as tf
import os
from my_imagenet_dataloader import get_imagenet_dataloader

def preprocess(image):
    image = tf.keras.applications.resnet50.preprocess_input(image)
    return tf.cast(image, dtype=tf.float32)

def get_dataloader(dataset_path_name, batch_size, quantization_samples):
    """
    This function should have this exact name and arguments. It is used for quantization to INT8.
    It should return a tf.data.Dataset object with the given batch_size and quantization_samples number of elements.
    Using tf.data.Dataset.repeat() is best to ensure enough samples.
    The dataset should not contain labels, only input data.
    The datasets sources should exist on the datasets directory.
    """
    ds_quant = get_imagenet_dataloader(dataset_path_name, batch_size)
    ds_quant = ds_quant.map(lambda x: preprocess(x))
    return ds_quant.repeat().take(quantization_samples)
