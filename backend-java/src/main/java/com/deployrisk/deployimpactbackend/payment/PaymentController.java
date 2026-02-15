package com.deployrisk.deployimpactbackend.payment;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.client.RestTemplate;

import java.util.Random;

@RestController
@RequestMapping("/payment")
public class PaymentController {

    @Autowired
    private RestTemplate restTemplate;

    private static final Random random = new Random();

    // Manual spike injection toggle
    private static volatile boolean forceSpike = false;

    // Track last spike time for cascade simulation
    private static volatile long lastSpikeTime = 0;

    // Base spike probability (10%)
    private static final double BASE_SPIKE_PROB = 0.10;

    // Pressure window (ms)
    private static final long PRESSURE_WINDOW = 2000;

    @GetMapping("/toggle-spike")
    public String toggleSpike() {
        forceSpike = !forceSpike;
        return "Force spike mode: " + forceSpike;
    }

    @GetMapping("/pay")
    public String pay(@RequestParam double amount) throws InterruptedException {

        int delay;
        boolean spike = false;

        long now = System.currentTimeMillis();

        // Check if upstream pressure exists (Order might have spiked recently)
        boolean underPressure = (now - lastSpikeTime) < PRESSURE_WINDOW;

        double spikeProbability = BASE_SPIKE_PROB;

        // Increase probability if under pressure
        if (underPressure) {
            spikeProbability = 0.35;  // 35% chance during cascade
        }

        if (forceSpike || random.nextDouble() < spikeProbability) {
            delay = 1500 + random.nextInt(1500); // 1.5s – 3s spike
            spike = true;
            lastSpikeTime = now;
        } else {
            delay = 100 + random.nextInt(150);   // 100ms – 250ms baseline
        }

        Thread.sleep(delay);

        String inventoryResponse = restTemplate.getForObject(
                "http://localhost:8080/inventory/check?item=book",
                String.class
        );

        System.out.println(
                "[PAYMENT] Delay=" + delay +
                        "ms | Spike=" + spike +
                        " | UnderPressure=" + underPressure
        );

        return "Payment processed: " + amount + " | " + inventoryResponse;
    }
}
