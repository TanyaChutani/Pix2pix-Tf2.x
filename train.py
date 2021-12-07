import sys
import argparse
import tensorflow as tf

from pix2pix.loss.metric import psnr
from pix2pix.model.pix2pix import PIX2PIX
from pix2pix.model.generator import Generator
from pix2pix.model.discriminator import Discriminator
from pix2pix.data.data_generator import DataGenerator

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('-gan_epoch',
                        '--epochs',
                        type=int,
                        metavar='',
                        default = 200)

    parser.add_argument('-b',
                        '--batch_size',
                        type=int,
                        metavar='',
                        default = 16)

    parser.add_argument('-img_dir',
                        '--train_path',
                        type=str,
                        metavar='',
                        default = '/pix2pix_tf/cityscapes/train/*.jpg')

    parser.add_argument('-w',
                        '--gan_weights_path',
                        type=str,
                        metavar='',
                        default = '/pix2pix_tf/weights/')
    args = parser.parse_args()
    return args

def main():
    args = parse_args()
    train_gen = DataGenerator(data_path=args.train_path)
    val_gen = DataGenerator(data_path=args.val_path)

    train_dataset = tf.data.Dataset.from_generator(train_gen,
                                                   output_types = (tf.float32, tf.float32),
                                                   output_shapes=([256, 256, 3], [256, 256, 3]))
    train_dataset = train_dataset.batch(args.batch_size)
    
    val_dataset = tf.data.Dataset.from_generator(val_gen, 
                                                 output_types = (tf.float32, tf.float32),
                                                 output_shapes=([256, 256, 3], [256, 256, 3]))
    val_dataset = val_dataset.batch(args.batch_size)
    
    learning_rate = tf.optimizers.schedules.PiecewiseConstantDecay(boundaries=[args.epochs / 2],
                                                                   values=[0.0001, 0.00001])
    callbacks = [tf.keras.callbacks.ModelCheckpoint(args.gan_weights_path,
                                                    monitor='loss',
                                                    save_best_only=False,
                                                    save_weights_only=True, 
                                                    mode='auto')]
    model = PIX2PIX()
    
    
    model.compile(generator_optimizer = tf.keras.optimizers.Adam(learning_rate),
                  discriminator_optimizer = tf.keras.optimizers.Adam(learning_rate),
                  loss = tf.keras.losses.MeanAbsoluteError(),
                  metric=psnr)
    model.fit(train_dataset,
              epochs=(args.epochs),
              validation_data=val_dataset)
    
if __name__ == "__main__":
    main()
