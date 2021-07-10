package com.virtualavator.preference

import android.content.Context
import android.content.SharedPreferences
import androidx.preference.PreferenceManager

class PreferenceUtils {
    companion object {
        fun isCameraLiveViewportEnabled(context: Context): Boolean {
            val sharedPreferences = PreferenceManager.getDefaultSharedPreferences(context);
            return sharedPreferences.getBoolean("isCameraLiveViewportEnabled", false)
        }

        fun shouldHideDetectionInfo(context: Context): Boolean {
            val sharedPreferences = PreferenceManager.getDefaultSharedPreferences(context);
            return sharedPreferences.getBoolean("shouldHideDetectionInfo", false)
        }
    }
}