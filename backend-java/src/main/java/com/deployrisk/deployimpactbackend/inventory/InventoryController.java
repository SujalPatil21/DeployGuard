package com.deployrisk.deployimpactbackend.inventory;

import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/inventory")
public class InventoryController {

    @GetMapping("/check")
    public String check(@RequestParam String item) {
        System.out.println("Inventory Service Hit");

        return "Inventory available for " + item;
    }
}
