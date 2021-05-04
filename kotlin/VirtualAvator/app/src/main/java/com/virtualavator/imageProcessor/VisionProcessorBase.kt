package com.virtualavator.imageProcessor

import android.app.ActivityManager
import android.content.Context
import android.graphics.Bitmap
import android.os.SystemClock
import android.util.Log
import android.widget.Toast
import androidx.annotation.GuardedBy
import androidx.camera.core.ExperimentalGetImage
import androidx.camera.core.ImageProxy
import com.google.android.gms.tasks.Task
import com.google.android.gms.tasks.TaskExecutors
import com.google.mlkit.vision.common.InputImage
import com.virtualavator.preference.PreferenceUtils
import com.virtualavator.utils.*
import java.nio.ByteBuffer
import java.util.*

abstract class VisionProcessorBase<T>(context: Context) : VisionImageProcessor {

    companion object {
        const val MANUAL_TESTING_LOG = "LogTagForTest"
        private const val TAG = "VisionProcessorBase"
    }

    private var activityManager: ActivityManager =
        context.getSystemService(Context.ACTIVITY_SERVICE) as ActivityManager
    private val fpsTimer = Timer()
    private val executor = ScopedExecutor(TaskExecutors.MAIN_THREAD)

    // Whether this processor is already shut down
    private var isShutdown = false

    // Used to calculate latency, running in the same thread, no sync needed.
    private var numRuns = 0
    private var totalFrameMs = 0L
    private var maxFrameMs = 0L
    private var minFrameMs = Long.MAX_VALUE
    private var totalDetectorMs = 0L
    private var maxDetectorMs = 0L
    private var minDetectorMs = Long.MAX_VALUE

    // Frame count that have been processed so far in an one second interval to calculate FPS.
    private var frameProcessedInOneSecondInterval = 0
    private var framesPerSecond = 0

    // To keep the latest images and its metadata.
    @GuardedBy("this")
    private var latestImage: ByteBuffer? = null
    @GuardedBy("this")
    private var latestImageMetaData: FrameMetadata? = null
    // To keep the images and metadata in process.
    @GuardedBy("this")
    private var processingImage: ByteBuffer? = null
    @GuardedBy("this")
    private var processingMetaData: FrameMetadata? = null

    init {
        fpsTimer.scheduleAtFixedRate(
            object : TimerTask() {
                override fun run() {
                    framesPerSecond = frameProcessedInOneSecondInterval
                    frameProcessedInOneSecondInterval = 0
                }
            },
            0,
            1000
        )
    }

    @ExperimentalGetImage
    override fun processImageProxy(image: ImageProxy, graphicOverlay: GraphicOverlay) {
        val frameStartMs = SystemClock.elapsedRealtime()
        if (isShutdown) {
            return
        }
        var bitmap: Bitmap? = null
        if (!PreferenceUtils.isCameraLiveViewportEnabled(graphicOverlay.context)) {
            bitmap = BitmapUtils.getBitmap(image)
        }
        requestDetectInImage(
            InputImage.fromMediaImage(image.image!!, image.imageInfo.rotationDegrees),
            graphicOverlay, /* originalCameraImage= */
            bitmap, /* shouldShowFps= */
            true,
            frameStartMs
        )
            // When the image is from CameraX analysis use case, must call image.close() on received
            // images when finished using them. Otherwise, new images may not be received or the camera
            // may stall.
            .addOnCompleteListener { image.close() }
    }

    private fun requestDetectInImage(
        image: InputImage,
        graphicOverlay: GraphicOverlay,
        originalCameraImage: Bitmap?,
        shouldShowFps: Boolean,
        frameStartMs: Long
    ): Task<T> {
        val detectorStartMs = SystemClock.elapsedRealtime()
        return detectInImage(image).addOnSuccessListener(executor) { results: T ->
            val endMs = SystemClock.elapsedRealtime()
            val currentFrameLatencyMs = endMs - frameStartMs
            val currentDetectorLatencyMs = endMs - detectorStartMs
            if (numRuns >= 500) {
                resetLatencyStats()
            }
            numRuns++
            frameProcessedInOneSecondInterval++
            totalFrameMs += currentFrameLatencyMs
            maxFrameMs = Math.max(currentFrameLatencyMs, maxFrameMs)
            minFrameMs = Math.min(currentFrameLatencyMs, minFrameMs)
            totalDetectorMs += currentDetectorLatencyMs
            maxDetectorMs = Math.max(currentDetectorLatencyMs, maxDetectorMs)
            minDetectorMs = Math.min(currentDetectorLatencyMs, minDetectorMs)

            // Only log inference info once per second. When frameProcessedInOneSecondInterval is
            // equal to 1, it means this is the first frame processed during the current second.
            if (frameProcessedInOneSecondInterval == 1) {
                Log.d(TAG, "Num of Runs: $numRuns")
                Log.d(
                    TAG,
                    "Frame latency: max=$maxFrameMs, min=$minFrameMs, avg=" +
                            (totalFrameMs / numRuns)
                )
                Log.d(
                    TAG,
                    "Detector latency: max=$maxDetectorMs, min=$minDetectorMs, avg=" +
                            (totalDetectorMs / numRuns)
                )
                val mi = ActivityManager.MemoryInfo()
                activityManager.getMemoryInfo(mi)
                val availableMegs = mi.availMem / 0x100000L
                Log.d(TAG, "Memory available in system: $availableMegs MB")
            }
            graphicOverlay.clear()
            if (originalCameraImage != null) {
                graphicOverlay.add(
                    CameraImageGraphic(
                        graphicOverlay,
                        originalCameraImage
                    )
                )
            }
            this@VisionProcessorBase.onSuccess(results, graphicOverlay)
            if (!PreferenceUtils.shouldHideDetectionInfo(graphicOverlay.context)) {
                graphicOverlay.add(
                    InferenceInfoGraphic(
                        graphicOverlay,
                        currentFrameLatencyMs,
                        currentDetectorLatencyMs,
                        if (shouldShowFps) framesPerSecond else null
                    )
                )
            }
            graphicOverlay.postInvalidate()
        }
            .addOnFailureListener(executor) { e: Exception ->
                graphicOverlay.clear()
                graphicOverlay.postInvalidate()
                Toast.makeText(
                    graphicOverlay.context,
                    "Failed to process.\nError: " +
                            e.localizedMessage +
                            "\nCause: " +
                            e.cause,
                    Toast.LENGTH_LONG
                )
                    .show()
                e.printStackTrace()
                this@VisionProcessorBase.onFailure(e)
            }
    }

    override fun stop() {
        executor.shutdown()
        isShutdown = true
        resetLatencyStats()
        fpsTimer.cancel()
    }

    private fun resetLatencyStats() {
        numRuns = 0
        totalFrameMs = 0
        maxFrameMs = 0
        minFrameMs = Long.MAX_VALUE
        totalDetectorMs = 0
        maxDetectorMs = 0
        minDetectorMs = Long.MAX_VALUE
    }

    protected abstract fun detectInImage(image: InputImage): Task<T>

    protected abstract fun onSuccess(results: T, graphicOverlay: GraphicOverlay)

    protected abstract fun onFailure(e: Exception)
}