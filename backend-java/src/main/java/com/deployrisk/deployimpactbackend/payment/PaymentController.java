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

    // Allows controlled spike injection
    private static volatile boolean forceSpike = false;

    @GetMapping("/toggle-spike")
    public String toggleSpike() {
        forceSpike = !forceSpike;
        return "Force spike mode: " + forceSpike;
    }

    @GetMapping("/pay")
    public String pay(@RequestParam double amount) throws InterruptedException {

        int delay;

        // 20% natural spike OR forced spike
        if (forceSpike || random.nextDouble() < 0.2) {
            delay = 1500 + random.nextInt(1500);  // 1.5s – 3s spike
        } else {
            delay = 100 + random.nextInt(150);   // 100ms – 250ms baseline
        }

        Thread.sleep(delay);

        String inventoryResponse = restTemplate.getForObject(
                "http://localhost:8080/inventory/check?item=book",
                String.class
        );

        System.out.println("[PAYMENT] Delay=" + delay + "ms | ForceSpike=" + forceSpike);

        return "Payment processed: " + amount + " | " + inventoryResponse;
    }
}
