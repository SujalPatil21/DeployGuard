    package com.deployrisk.deployimpactbackend.payment;

    import org.springframework.beans.factory.annotation.Autowired;
    import org.springframework.web.bind.annotation.*;
    import org.springframework.web.client.RestTemplate;

    @RestController
    @RequestMapping("/payment")
    public class PaymentController {

        @Autowired
        private RestTemplate restTemplate;

        @GetMapping("/pay")
        public String pay(@RequestParam double amount) throws InterruptedException {
            Thread.sleep(400);
            String inventoryResponse = restTemplate.getForObject(
                    "http://localhost:8080/inventory/check?item=book",
                    String.class
            );

            System.out.println("Payment Service Hit");

            return "Payment processed: " + amount + " | " + inventoryResponse;
        }
    }
