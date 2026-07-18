package com.example.order.service;

import org.springframework.stereotype.Service;
import com.example.order.client.PaymentClient;

@Service
public class OrderService {

    private final PaymentClient paymentClient;

    public OrderService(PaymentClient paymentClient) {
        this.paymentClient = paymentClient;
    }

    public Order createOrder(CreateOrderRequest request) {
        Order order = new Order();
        order.setStatus("CREATED");
        paymentClient.createPayment(order.getId(), request.getAmount());
        return order;
    }

    public Order getOrderById(Long id) {
        return null;
    }

    public Order updateOrderStatus(Long id, String status) {
        return null;
    }
}
