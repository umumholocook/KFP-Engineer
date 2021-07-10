package com.virtualavator.utils

import com.google.android.datatransport.runtime.ExecutionModule_ExecutorFactory.executor
import java.util.concurrent.Executor
import java.util.concurrent.atomic.AtomicBoolean


class ScopedExecutor(private val executor: Executor) : Executor {

    private val shutdown = AtomicBoolean()

    override fun execute(command: Runnable) {
        if (shutdown.get()) {
            return;
        }
        executor.execute {
            // Check again in case it has been shut down in the mean time.
            if (!shutdown.get()) {
                command.run()
            }
        }
    }

    fun shutdown() {
        shutdown.set(true)
    }
}