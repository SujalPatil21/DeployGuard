package com.deployrisk.deployimpactbackend.inventory;

import org.springframework.web.bind.annotation.*;

import java.util.Random;

@RestController
@RequestMapping("/inventory")
public class InventoryController {

    private static final Random random = new Random();

    // Track last spike time
    private static volatile long lastSpikeTime = 0;

    // Base spike probability (8%)
    private static final double BASE_SPIKE_PROB = 0.08;

    // Cascade pressure window (ms)
    private static final long PRESSURE_WINDOW = 2000;

    @GetMapping("/check")
    public String check(@RequestParam String item) throws InterruptedException {

        int delay;
        boolean spike = false;

        long now = System.currentTimeMillis();

        // Check if Payment spiked recently
        boolean underPressure = (now - lastSpikeTime) < PRESSURE_WINDOW;

        double spikeProbability = BASE_SPIKE_PROB;

        if (underPressure) {
            spikeProbability = 0.30; // Higher chance during cascade
        }

        if (random.nextDouble() < spikeProbability) {
            delay = 1200 + random.nextInt(1200); // 1.2s – 2.4s spike
            spike = true;
            lastSpikeTime = now;
        } else {
            delay = 80 + random.nextInt(120); // 80ms – 200ms baseline
        }

        Thread.sleep(delay);

        System.out.println(
                "[INVENTORY] Delay=" + delay +
                        "ms | Spike=" + spike +
                        " | UnderPressure=" + underPressure
        );

        return "Inventory available for " + item;
    }
}
