package com.example.order.client;

import org.springframework.cloud.openfeign.FeignClient;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestParam;

@FeignClient(name = "payment-service", url = "${payment.service.url}")
public interface PaymentClient {

    @PostMapping("/api/payments")
    PaymentResponse createPayment(@RequestParam Long orderId, @RequestParam Double amount);

    @GetMapping("/api/payments/{orderId}")
    PaymentResponse getPaymentStatus(@RequestParam Long orderId);
}
