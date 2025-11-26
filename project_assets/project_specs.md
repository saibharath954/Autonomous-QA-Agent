# 📘 Product Specifications — E-Shop Checkout System

This document defines the complete functional rules for the E-Shop Checkout System used for QA testing, automation, and RAG-based validation.

---

## 1. Discount Code Rules

### Supported Codes
| Code | Description | Effect |
|------|-------------|--------|
| SAVE15 | Percentage discount | Applies **15% discount** on subtotal |
| FREESHIP | Shipping discount | Shipping fee becomes **$0** |

### Validation Rules
- Only **one discount code** may be applied at a time.
- Invalid codes must display:  
  **"Invalid Code"** (inline message)
- The discount applies **before shipping**.

---

## 2. Shipping Rules

### Options
- **Standard Shipping**
  - Cost: ₹0 / $0
  - Delivery: 5–7 business days
- **Express Shipping**
  - Cost: ₹800 / $10
  - Delivery: 1–2 business days

### Calculation Rule

final_total = subtotal - discount + shipping_fee

---

## 3. Cart Logic Rules
- Minimum quantity: **1**
- Update button recalculates subtotal.
- Subtotal is: Σ (item_price × quantity)


---

## 4. User Details Rules

| Field | Requirement |
|--------|-------------|
| Full Name | Required, ≥ 3 characters |
| Email | Must match regex: `^\S+@\S+\.\S+$` |
| Address | Required |
| Phone | Optional, but if present must be **10 digits** |

Errors must appear inline and in red (`#FF0000`).

---

## 5. UI Validation & Success States

### Errors
- Display in red (#FF0000)
- Must appear inline beside fields

### Success
- When payment is successful, show: Payment Successful!
- Form may optionally be hidden after success

---

## 6. Payment

Supported:
- Credit Card
- PayPal
