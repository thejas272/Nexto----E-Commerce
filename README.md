# Nexto----E-Commerce
A full-stack e-commerce platform built using Django, designed with real-world features such as cart management, address handling, online payments, and order lifecycle management.

Key Features


E-Commerce Functionality

  Product listing with categories 
  Product search, filtering, and detail pages
  Add to cart, update quantity, remove items
  Delivery address management with default address logic
  Order summary & checkout flow


Secure Razorpay Payment Gateway

  Razorpay order creation (server-side)
  Signature verification on backend
  Prevention of duplicate order creation


Order & Return System
  
  Automatic order creation after successful payment
  Category-based return window:


User Account & Address System

  Multiple addresses per user
  Only one default address allowed (auto-managed)
  Edit, delete, set-default options
  Pre-filled address for checkout


Cart & Checkout

  Dynamic cart total calculation
  Handling fee + shipping fee rules
  Coupon-ready architecture
  Razorpay + COD payment options


Security & Best Practices

  Server-side signature verification
  Model methods and validation checks
  Preventing duplicate order creation


Tech Stack
  
  Backend
  
  Python
  Django
  Django ORM
  PostgreSQL

  Frontend

  HTML, CSS, Bootstrap 5

  

    
  
  
