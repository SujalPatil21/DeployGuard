package com.deployrisk.deployimpactbackend.order;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.client.RestTemplate;

@RestController
@RequestMapping("/order")
public class OrderController {

    @Autowired
    private RestTemplate restTemplate;

    @GetMapping("/create")
    public String createOrder(@RequestParam String item) {

        String paymentResponse = restTemplate.getForObject(
                "http://localhost:8080/payment/pay?amount=100",
                String.class
        );
        System.out.println("Order Service Hit");

        return "Order created for " + item + " | " + paymentResponse;

    }
}
