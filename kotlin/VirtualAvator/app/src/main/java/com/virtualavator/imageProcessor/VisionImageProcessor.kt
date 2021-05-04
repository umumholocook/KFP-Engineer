package com.virtualavator.imageProcessor

import android.os.Build
import androidx.annotation.RequiresApi
import com.google.mlkit.common.MlKitException
import androidx.camera.core.ImageProxy
import com.virtualavator.utils.GraphicOverlay
import kotlin.jvm.Throws

interface VisionImageProcessor {

    @RequiresApi(Build.VERSION_CODES.KITKAT)
    @Throws(MlKitException::class)
    fun processImageProxy(image: ImageProxy, graphicOverlay: GraphicOverlay)

    fun stop()
}