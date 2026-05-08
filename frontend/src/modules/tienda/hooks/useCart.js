import { useState, useEffect } from 'react';

export const useCart = () => {
    const [cart, setCart] = useState(() => {
        const saved = localStorage.getItem('miqhatu_cart');
        return saved ? JSON.parse(saved) : [];
    });

    useEffect(() => {
        localStorage.setItem('miqhatu_cart', JSON.stringify(cart));
    }, [cart]);

    const addToCart = (product) => {
        setCart(prev => {
            const exists = prev.find(item => item.id === product.id);
            if (exists) {
                return prev.map(item => 
                    item.id === product.id 
                    ? { ...item, quantity: item.quantity + 1 } 
                    : item
                );
            }
            return [...prev, { ...product, quantity: 1 }];
        });
    };

    const removeFromCart = (id) => {
        setCart(prev => prev.filter(item => item.id !== id));
    };

    const updateQuantity = (id, delta) => {
        setCart(prev => prev.map(item => {
            if (item.id === id) {
                const newQty = Math.max(1, item.quantity + delta);
                return { ...item, quantity: newQty };
            }
            return item;
        }));
    };

    const clearCart = () => setCart([]);

    const total = cart.reduce((acc, item) => acc + (item.precio * item.quantity), 0);

    return {
        cart,
        addToCart,
        removeFromCart,
        updateQuantity,
        clearCart,
        total
    };
};
