package com.deployrisk.deployimpactbackend.auth;

import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/auth")
public class AuthController {

    @GetMapping("/login")
    public String login(@RequestParam String user) {
        return "Auth OK for " + user;
    }
}
