package com.deployrisk.deployimpactbackend.order;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.client.RestTemplate;

import java.util.Random;

@RestController
@RequestMapping("/order")
public class OrderController {

    @Autowired
    private RestTemplate restTemplate;

    private static final Random random = new Random();

    private static volatile long lastSpikeTime = 0;

    private static final double BASE_SPIKE_PROB = 0.10;
    private static final long PRESSURE_WINDOW = 2000;

    @GetMapping("/create")
    public String createOrder(@RequestParam String item) throws InterruptedException {

        int delay;
        boolean spike = false;

        long now = System.currentTimeMillis();
        boolean underPressure = (now - lastSpikeTime) < PRESSURE_WINDOW;

        double spikeProbability = BASE_SPIKE_PROB;

        if (underPressure) {
            spikeProbability = 0.35; // Amplified under pressure
        }

        if (random.nextDouble() < spikeProbability) {
            delay = 1000 + random.nextInt(1500); // 1s – 2.5s spike
            spike = true;
            lastSpikeTime = now;
        } else {
            delay = 100 + random.nextInt(150); // 100ms – 250ms baseline
        }

        Thread.sleep(delay);

        String paymentResponse = restTemplate.getForObject(
                "http://localhost:8080/payment/pay?amount=100",
                String.class
        );

        System.out.println(
                "[ORDER] Delay=" + delay +
                        "ms | Spike=" + spike +
                        " | UnderPressure=" + underPressure
        );

        return "Order created for " + item + " | " + paymentResponse;
    }
}
