package com.example.order.enums;

public enum OrderStatus {
    PENDING("pending", "待处理"),
    PROCESSING("processing", "处理中"),
    COMPLETED("completed", "已完成"),
    CANCELLED("cancelled", "已取消");

    private final String code;
    private final String label;

    OrderStatus(String code, String label) {
        this.code = code;
        this.label = label;
    }

    public String getCode() { return code; }
    public String getLabel() { return label; }
}
