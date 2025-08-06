#!/usr/bin/env python3
"""
Test suite for the binomial tree options pricing calculator
"""

import unittest
import numpy as np
from options_pricing import BinomialTreePricer, OptionParameters, black_scholes_comparison


class TestBinomialTreePricer(unittest.TestCase):
    """Test cases for the BinomialTreePricer class"""
    
    def setUp(self):
        """Set up test parameters"""
        self.standard_params = OptionParameters(
            S0=100,
            K=100,
            T=1.0,
            r=0.05,
            sigma=0.2,
            n=100,
            option_type='call',
            exercise_type='european'
        )
    
    def test_parameter_validation(self):
        """Test parameter validation"""
        # Test negative stock price
        with self.assertRaises(ValueError):
            params = OptionParameters(S0=-100, K=100, T=1, r=0.05, sigma=0.2, n=50, option_type='call')
            BinomialTreePricer(params)
        
        # Test negative strike price
        with self.assertRaises(ValueError):
            params = OptionParameters(S0=100, K=-100, T=1, r=0.05, sigma=0.2, n=50, option_type='call')
            BinomialTreePricer(params)
        
        # Test negative time to expiration
        with self.assertRaises(ValueError):
            params = OptionParameters(S0=100, K=100, T=-1, r=0.05, sigma=0.2, n=50, option_type='call')
            BinomialTreePricer(params)
        
        # Test negative volatility
        with self.assertRaises(ValueError):
            params = OptionParameters(S0=100, K=100, T=1, r=0.05, sigma=-0.2, n=50, option_type='call')
            BinomialTreePricer(params)
        
        # Test non-positive number of steps
        with self.assertRaises(ValueError):
            params = OptionParameters(S0=100, K=100, T=1, r=0.05, sigma=0.2, n=0, option_type='call')
            BinomialTreePricer(params)
    
    def test_payoff_calculation(self):
        """Test option payoff calculations"""
        pricer = BinomialTreePricer(self.standard_params)
        
        # Test call option payoff
        self.assertEqual(pricer._payoff(110), 10)  # In the money
        self.assertEqual(pricer._payoff(90), 0)    # Out of the money
        self.assertEqual(pricer._payoff(100), 0)   # At the money
        
        # Test put option payoff
        put_params = self.standard_params
        put_params.option_type = 'put'
        put_pricer = BinomialTreePricer(put_params)
        
        self.assertEqual(put_pricer._payoff(90), 10)   # In the money
        self.assertEqual(put_pricer._payoff(110), 0)   # Out of the money
        self.assertEqual(put_pricer._payoff(100), 0)   # At the money
    
    def test_stock_tree_construction(self):
        """Test stock price tree construction"""
        pricer = BinomialTreePricer(self.standard_params)
        stock_tree = pricer.build_stock_tree()
        
        # Check tree dimensions
        n = self.standard_params.n
        self.assertEqual(stock_tree.shape, (n + 1, n + 1))
        
        # Check initial stock price
        self.assertAlmostEqual(stock_tree[0, 0], self.standard_params.S0, places=5)
        
        # Check that stock prices are positive
        for i in range(n + 1):
            for j in range(i + 1):
                self.assertGreater(stock_tree[j, i], 0)
    
    def test_european_call_pricing(self):
        """Test European call option pricing"""
        pricer = BinomialTreePricer(self.standard_params)
        price, _ = pricer.price_option()
        
        # Price should be positive
        self.assertGreater(price, 0)
        
        # Compare with Black-Scholes (if scipy is available)
        try:
            bs_price = black_scholes_comparison(self.standard_params)
            # Binomial tree should converge to Black-Scholes with enough steps
            self.assertAlmostEqual(price, bs_price, delta=0.5)
        except ImportError:
            pass  # Skip if scipy not available
    
    def test_european_put_pricing(self):
        """Test European put option pricing"""
        put_params = OptionParameters(
            S0=100, K=100, T=1, r=0.05, sigma=0.2, n=100,
            option_type='put', exercise_type='european'
        )
        
        pricer = BinomialTreePricer(put_params)
        price, _ = pricer.price_option()
        
        # Price should be positive
        self.assertGreater(price, 0)
        
        # Compare with Black-Scholes (if scipy is available)
        try:
            bs_price = black_scholes_comparison(put_params)
            self.assertAlmostEqual(price, bs_price, delta=0.5)
        except ImportError:
            pass
    
    def test_american_vs_european_put(self):
        """Test that American put >= European put (early exercise premium)"""
        # American put
        american_params = OptionParameters(
            S0=90, K=100, T=1, r=0.05, sigma=0.3, n=50,
            option_type='put', exercise_type='american'
        )
        american_pricer = BinomialTreePricer(american_params)
        american_price, _ = american_pricer.price_option()
        
        # European put
        european_params = american_params
        european_params.exercise_type = 'european'
        european_pricer = BinomialTreePricer(european_params)
        european_price, _ = european_pricer.price_option()
        
        # American put should be worth at least as much as European put
        self.assertGreaterEqual(american_price, european_price)
    
    def test_put_call_parity(self):
        """Test put-call parity for European options"""
        # Call option
        call_params = OptionParameters(
            S0=100, K=100, T=1, r=0.05, sigma=0.2, n=100,
            option_type='call', exercise_type='european'
        )
        call_pricer = BinomialTreePricer(call_params)
        call_price, _ = call_pricer.price_option()
        
        # Put option
        put_params = call_params
        put_params.option_type = 'put'
        put_pricer = BinomialTreePricer(put_params)
        put_price, _ = put_pricer.price_option()
        
        # Put-call parity: C - P = S - K*e^(-r*T)
        S, K, T, r = call_params.S0, call_params.K, call_params.T, call_params.r
        parity_diff = call_price - put_price
        expected_diff = S - K * np.exp(-r * T)
        
        self.assertAlmostEqual(parity_diff, expected_diff, delta=0.1)
    
    def test_greeks_calculation(self):
        """Test Greeks calculation"""
        pricer = BinomialTreePricer(self.standard_params)
        greeks = pricer.calculate_greeks()
        
        # Check that all Greeks are present
        expected_greeks = ['delta', 'gamma', 'theta', 'vega', 'rho']
        for greek in expected_greeks:
            self.assertIn(greek, greeks)
        
        # Check reasonable values for call option
        self.assertGreater(greeks['delta'], 0)  # Call delta should be positive
        self.assertGreater(greeks['vega'], 0)   # Vega should be positive
        self.assertLess(greeks['theta'], 0)     # Theta should be negative (time decay)
    
    def test_extreme_parameters(self):
        """Test pricing with extreme parameters"""
        # Very high volatility
        high_vol_params = OptionParameters(
            S0=100, K=100, T=1, r=0.05, sigma=1.0, n=50,
            option_type='call', exercise_type='european'
        )
        pricer = BinomialTreePricer(high_vol_params)
        price, _ = pricer.price_option()
        self.assertGreater(price, 0)
        
        # Very short time to expiration
        short_time_params = OptionParameters(
            S0=100, K=100, T=0.01, r=0.05, sigma=0.2, n=10,
            option_type='call', exercise_type='european'
        )
        pricer = BinomialTreePricer(short_time_params)
        price, _ = pricer.price_option()
        self.assertGreater(price, 0)


def run_pricing_examples():
    """Run comprehensive pricing examples"""
    print("=" * 60)
    print("COMPREHENSIVE OPTIONS PRICING EXAMPLES")
    print("=" * 60)
    
    # Example 1: At-the-money European call
    print("\n1. At-the-Money European Call Option")
    print("-" * 40)
    call_params = OptionParameters(
        S0=100, K=100, T=0.25, r=0.05, sigma=0.2, n=100,
        option_type='call', exercise_type='european'
    )
    
    call_pricer = BinomialTreePricer(call_params)
    call_price, _ = call_pricer.price_option()
    call_greeks = call_pricer.calculate_greeks()
    
    print(f"Stock Price: ${call_params.S0}")
    print(f"Strike Price: ${call_params.K}")
    print(f"Time to Expiration: {call_params.T} years")
    print(f"Risk-free Rate: {call_params.r:.1%}")
    print(f"Volatility: {call_params.sigma:.1%}")
    print(f"Option Price: ${call_price:.4f}")
    print("Greeks:")
    for greek, value in call_greeks.items():
        print(f"  {greek.capitalize()}: {value:.4f}")
    
    # Example 2: Deep in-the-money American put
    print("\n2. Deep In-the-Money American Put Option")
    print("-" * 40)
    put_params = OptionParameters(
        S0=80, K=100, T=0.5, r=0.03, sigma=0.25, n=100,
        option_type='put', exercise_type='american'
    )
    
    put_pricer = BinomialTreePricer(put_params)
    put_price, _ = put_pricer.price_option()
    
    # Compare with European put
    put_params.exercise_type = 'european'
    european_put_pricer = BinomialTreePricer(put_params)
    european_put_price, _ = european_put_pricer.price_option()
    
    print(f"Stock Price: ${put_params.S0}")
    print(f"Strike Price: ${put_params.K}")
    print(f"American Put Price: ${put_price:.4f}")
    print(f"European Put Price: ${european_put_price:.4f}")
    print(f"Early Exercise Premium: ${put_price - european_put_price:.4f}")
    
    # Example 3: Out-of-the-money call with high volatility
    print("\n3. Out-of-the-Money Call with High Volatility")
    print("-" * 40)
    otm_params = OptionParameters(
        S0=90, K=110, T=0.75, r=0.04, sigma=0.4, n=150,
        option_type='call', exercise_type='european'
    )
    
    otm_pricer = BinomialTreePricer(otm_params)
    otm_price, _ = otm_pricer.price_option()
    otm_greeks = otm_pricer.calculate_greeks()
    
    print(f"Stock Price: ${otm_params.S0}")
    print(f"Strike Price: ${otm_params.K}")
    print(f"Volatility: {otm_params.sigma:.1%}")
    print(f"Option Price: ${otm_price:.4f}")
    print(f"Delta: {otm_greeks['delta']:.4f}")
    print(f"Vega: {otm_greeks['vega']:.4f}")
    
    # Example 4: Convergence test
    print("\n4. Convergence Test (Binomial vs Black-Scholes)")
    print("-" * 40)
    convergence_params = OptionParameters(
        S0=105, K=100, T=0.25, r=0.05, sigma=0.2, n=50,
        option_type='call', exercise_type='european'
    )
    
    steps = [10, 25, 50, 100, 200]
    print("Steps\tBinomial Price\tDifference from BS")
    
    try:
        bs_price = black_scholes_comparison(convergence_params)
        for n in steps:
            convergence_params.n = n
            pricer = BinomialTreePricer(convergence_params)
            price, _ = pricer.price_option()
            diff = abs(price - bs_price)
            print(f"{n}\t${price:.4f}\t\t${diff:.4f}")
        print(f"Black-Scholes: ${bs_price:.4f}")
    except ImportError:
        print("SciPy not available for Black-Scholes comparison")


if __name__ == "__main__":
    # Run unit tests
    print("Running unit tests...")
    unittest.main(argv=[''], exit=False, verbosity=2)
    
    # Run pricing examples
    run_pricing_examples()