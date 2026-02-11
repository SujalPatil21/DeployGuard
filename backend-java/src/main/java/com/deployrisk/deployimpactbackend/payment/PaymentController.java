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

    @GetMapping("/pay")
    public String pay(@RequestParam double amount) throws InterruptedException {

        int delay;

        if (random.nextDouble() < 0.80) {
            // 40% heavy spike
            delay = 1500 + random.nextInt(1500);  // 1.5s – 3s
        } else {
            // Faster normal baseline
            delay = 100 + random.nextInt(150);   // 100ms – 250ms
        }


        Thread.sleep(delay);


        String inventoryResponse = restTemplate.getForObject(
                "http://localhost:8080/inventory/check?item=book",
                String.class
        );

        System.out.println("Payment Service Hit | Delay: " + delay + " ms");

        return "Payment processed: " + amount + " | " + inventoryResponse;
    }
}
