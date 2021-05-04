package com.virtualavator.utils

import android.graphics.Canvas
import android.graphics.Color
import android.graphics.Paint
import com.virtualavator.utils.GraphicOverlay.Graphic

/** Graphic instance for rendering inference info (latency, FPS, resolution) in an overlay view.  */
class InferenceInfoGraphic(
    private val overlay: GraphicOverlay,
    private val frameLatency: Long,
    private val detectorLatency: Long,
    // Only valid when a stream of input images is being processed. Null for single image mode.
    private val framesPerSecond: Int?
) : Graphic(overlay) {
    private val textPaint: Paint
    private var showLatencyInfo = true

    /** Creates an [InferenceInfoGraphic] to only display image size.  */
    constructor(overlay: GraphicOverlay) : this(overlay, 0, 0, null) {
        showLatencyInfo = false
    }

    @Synchronized
    override fun draw(canvas: Canvas?) {
        val x = TEXT_SIZE * 0.5f
        val y = TEXT_SIZE * 1.5f
        canvas?.drawText(
            "InputImage size: " + overlay.imageHeight + "x" + overlay.imageWidth,
            x,
            y,
            textPaint
        )
        if (!showLatencyInfo) {
            return
        }
        // Draw FPS (if valid) and inference latency
        if (framesPerSecond != null) {
            canvas?.drawText(
                "FPS: $framesPerSecond, Frame latency: $frameLatency ms",
                x,
                y + TEXT_SIZE,
                textPaint
            )
        } else {
            canvas?.drawText("Frame latency: $frameLatency ms", x, y + TEXT_SIZE, textPaint)
        }
        canvas?.drawText(
            "Detector latency: $detectorLatency ms", x, y + TEXT_SIZE * 2, textPaint
        )
    }

    companion object {
        private val TEXT_COLOR: Int = Color.WHITE
        private const val TEXT_SIZE = 60.0f
    }

    init {
        textPaint = Paint()
        textPaint.setColor(TEXT_COLOR)
        textPaint.setTextSize(TEXT_SIZE)
        textPaint.setShadowLayer(5.0f, 0f, 0f, Color.BLACK)
        postInvalidate()
    }
}