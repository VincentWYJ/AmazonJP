# -*- coding: utf-8 -*-


import image
import shutil
import os


class Graphics:

    @classmethod
    def fixed_size(source_image,destination_image, width, height):
        """按照固定尺寸处理图片"""
        im = image.open(source_image)
        out = im.resize((width, height),image.ANTIALIAS)
        out.save(destination_image)

    @classmethod
    def resize_by_width(source_image,destination_image, w_divide_h):
        """按照宽度进行所需比例缩放"""
        im = image.open(source_image)
        (x, y) = im.size
        x_s = x
        y_s = x/w_divide_h
        out = im.resize((x_s, y_s), image.ANTIALIAS)
        out.save(destination_image)

    @classmethod
    def resize_by_height(source_image,destination_image, w_divide_h):
        """按照高度进行所需比例缩放"""
        im = image.open(source_image)
        (x, y) = im.size
        x_s = y*w_divide_h
        y_s = y
        out = im.resize((x_s, y_s), image.ANTIALIAS)
        out.save(destination_image)

    @classmethod
    def resize_by_size(source_image,destination_image, size):
        """按照生成图片文件大小进行处理(单位KB)"""
        size *= 1024
        im = image.open(source_image)
        size_tmp = os.path.getsize(source_image)
        q = 100
        while size_tmp > size and q > 0:
            out = im.resize(im.size, image.ANTIALIAS)
            out.save(destination_image, quality=q)
            size_tmp = os.path.getsize(destination_image)
            q -= 5
        if q == 100:
            shutil.copy(source_image, destination_image)

    @classmethod
    def cut_by_ratio(source_image,destination_image, width, height):
        """按照图片长宽比进行分割"""
        im = image.open(source_image)
        width = float(width)
        height = float(height)
        (x, y) = im.size
        if width > height:
            region = (0, int((y-(yi * (height / width)))/2), x, int((y+(y * (height / width)))/2))
        elif width < height:
            region = (int((x-(x * (width / height)))/2), 0, int((x+(x * (width / height)))/2), y)
        else:
            region = (0, 0, x, y)

        #裁切图片
        crop_img = im.crop(region)
        #保存裁切后的图片
        crop_img.save(destination_image)