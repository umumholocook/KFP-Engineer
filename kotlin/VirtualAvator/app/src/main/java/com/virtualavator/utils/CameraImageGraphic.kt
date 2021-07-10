package com.virtualavator.utils

import android.graphics.Bitmap
import android.graphics.Canvas

class CameraImageGraphic(overlay: GraphicOverlay, private val bitmap: Bitmap): GraphicOverlay.Graphic(overlay) {

    override fun draw(canvas: Canvas?) {
        canvas?.drawBitmap(bitmap, getTransformationMatrix(), null)
    }
}