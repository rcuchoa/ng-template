#!/usr/bin/env python3
"""
Simplified Binomial Tree Options Pricing Calculator
Uses only Python built-in libraries for demonstration
"""

import math
from typing import Literal, Tuple
from dataclasses import dataclass


@dataclass
class OptionParameters:
    """
    Data class to hold option parameters
    """
    S0: float           # Current stock price
    K: float            # Strike price
    T: float            # Time to expiration (in years)
    r: float            # Risk-free rate
    sigma: float        # Volatility
    n: int              # Number of time steps
    option_type: Literal['call', 'put']  # Option type
    exercise_type: Literal['european', 'american'] = 'european'  # Exercise type


class SimpleBinomialTreePricer:
    """
    Simplified Binomial Tree Options Pricing Calculator
    
    This class implements the Cox-Ross-Rubinstein (CRR) binomial tree model
    for pricing both European and American options using only built-in Python libraries.
    """
    
    def __init__(self, params: OptionParameters):
        """
        Initialize the binomial tree pricer with option parameters
        
        Args:
            params: OptionParameters object containing all option details
        """
        self.params = params
        self.dt = params.T / params.n  # Time step size
        
        # Calculate binomial tree parameters using CRR model
        self.u = math.exp(params.sigma * math.sqrt(self.dt))  # Up factor
        self.d = 1 / self.u  # Down factor
        self.p = (math.exp(params.r * self.dt) - self.d) / (self.u - self.d)  # Risk-neutral probability
        self.discount_factor = math.exp(-params.r * self.dt)  # Discount factor
        
        # Validate parameters
        self._validate_parameters()
    
    def _validate_parameters(self) -> None:
        """Validate input parameters"""
        if self.params.S0 <= 0:
            raise ValueError("Current stock price must be positive")
        if self.params.K <= 0:
            raise ValueError("Strike price must be positive")
        if self.params.T <= 0:
            raise ValueError("Time to expiration must be positive")
        if self.params.sigma <= 0:
            raise ValueError("Volatility must be positive")
        if self.params.n <= 0:
            raise ValueError("Number of steps must be positive")
        if not 0 < self.p < 1:
            raise ValueError("Risk-neutral probability must be between 0 and 1")
    
    def _payoff(self, S: float) -> float:
        """
        Calculate option payoff at expiration
        
        Args:
            S: Stock price at expiration
            
        Returns:
            Option payoff
        """
        if self.params.option_type == 'call':
            return max(S - self.params.K, 0)
        else:  # put
            return max(self.params.K - S, 0)
    
    def _early_exercise_value(self, S: float) -> float:
        """
        Calculate early exercise value for American options
        
        Args:
            S: Current stock price
            
        Returns:
            Early exercise value
        """
        return self._payoff(S)
    
    def build_stock_tree(self) -> list:
        """
        Build the stock price tree using nested lists
        
        Returns:
            2D list containing stock prices at each node
        """
        n = self.params.n
        stock_tree = [[0.0 for _ in range(n + 1)] for _ in range(n + 1)]
        
        for i in range(n + 1):
            for j in range(i + 1):
                stock_tree[j][i] = self.params.S0 * (self.u ** (i - j)) * (self.d ** j)
        
        return stock_tree
    
    def price_option(self) -> Tuple[float, list]:
        """
        Price the option using binomial tree method
        
        Returns:
            Tuple of (option_price, option_tree)
        """
        n = self.params.n
        
        # Build stock price tree
        stock_tree = self.build_stock_tree()
        
        # Initialize option value tree
        option_tree = [[0.0 for _ in range(n + 1)] for _ in range(n + 1)]
        
        # Calculate option values at expiration (final column)
        for j in range(n + 1):
            option_tree[j][n] = self._payoff(stock_tree[j][n])
        
        # Work backwards through the tree
        for i in range(n - 1, -1, -1):
            for j in range(i + 1):
                # Calculate expected option value
                expected_value = self.discount_factor * (
                    self.p * option_tree[j][i + 1] + 
                    (1 - self.p) * option_tree[j + 1][i + 1]
                )
                
                if self.params.exercise_type == 'american':
                    # For American options, check early exercise
                    early_exercise = self._early_exercise_value(stock_tree[j][i])
                    option_tree[j][i] = max(expected_value, early_exercise)
                else:
                    # For European options, no early exercise
                    option_tree[j][i] = expected_value
        
        return option_tree[0][0], option_tree
    
    def display_tree_sample(self, tree: list, tree_type: str = "Stock Price") -> None:
        """
        Display a sample of the tree for visualization
        
        Args:
            tree: The tree to display (stock prices or option values)
            tree_type: Type of tree being displayed
        """
        n = min(5, self.params.n)  # Show only first 5 steps for readability
        
        print(f"\n{tree_type} Tree (first {n+1} steps):")
        print("-" * 50)
        
        for i in range(n + 1):
            print(f"Step {i}: ", end="")
            for j in range(i + 1):
                print(f"{tree[j][i]:8.2f} ", end="")
            print()


def black_scholes_simple(S: float, K: float, T: float, r: float, sigma: float, option_type: str) -> float:
    """
    Simplified Black-Scholes implementation using built-in math functions
    Note: This approximates the normal distribution CDF
    
    Args:
        S: Current stock price
        K: Strike price
        T: Time to expiration
        r: Risk-free rate
        sigma: Volatility
        option_type: 'call' or 'put'
        
    Returns:
        Black-Scholes option price (approximation)
    """
    
    def norm_cdf_approx(x: float) -> float:
        """Approximate normal CDF using Abramowitz and Stegun formula"""
        # Constants for approximation
        a1 =  0.254829592
        a2 = -0.284496736
        a3 =  1.421413741
        a4 = -1.453152027
        a5 =  1.061405429
        p  =  0.3275911
        
        # Save the sign of x
        sign = 1 if x >= 0 else -1
        x = abs(x) / math.sqrt(2.0)
        
        # A&S formula 7.1.26
        t = 1.0 / (1.0 + p * x)
        y = 1.0 - (((((a5 * t + a4) * t) + a3) * t + a2) * t + a1) * t * math.exp(-x * x)
        
        return 0.5 * (1.0 + sign * y)
    
    d1 = (math.log(S/K) + (r + 0.5 * sigma**2) * T) / (sigma * math.sqrt(T))
    d2 = d1 - sigma * math.sqrt(T)
    
    if option_type == 'call':
        price = S * norm_cdf_approx(d1) - K * math.exp(-r * T) * norm_cdf_approx(d2)
    else:  # put
        price = K * math.exp(-r * T) * norm_cdf_approx(-d2) - S * norm_cdf_approx(-d1)
    
    return price


def run_simple_examples():
    """Run examples using the simplified implementation"""
    print("=" * 70)
    print("SIMPLE BINOMIAL TREE OPTIONS PRICING EXAMPLES")
    print("=" * 70)
    
    # Example 1: European Call Option
    print("\n1. European Call Option")
    print("-" * 40)
    call_params = OptionParameters(
        S0=100,          # Current stock price
        K=105,           # Strike price
        T=0.25,          # 3 months to expiration
        r=0.05,          # 5% risk-free rate
        sigma=0.2,       # 20% volatility
        n=10,            # 10 time steps for simplicity
        option_type='call',
        exercise_type='european'
    )
    
    call_pricer = SimpleBinomialTreePricer(call_params)
    call_price, call_tree = call_pricer.price_option()
    
    print(f"Parameters:")
    print(f"  Stock Price: ${call_params.S0}")
    print(f"  Strike Price: ${call_params.K}")
    print(f"  Time to Expiration: {call_params.T} years")
    print(f"  Risk-free Rate: {call_params.r:.1%}")
    print(f"  Volatility: {call_params.sigma:.1%}")
    print(f"  Number of Steps: {call_params.n}")
    
    print(f"\nResults:")
    print(f"  Binomial Tree Price: ${call_price:.4f}")
    
    # Compare with Black-Scholes approximation
    bs_price = black_scholes_simple(
        call_params.S0, call_params.K, call_params.T, 
        call_params.r, call_params.sigma, call_params.option_type
    )
    print(f"  Black-Scholes (approx): ${bs_price:.4f}")
    print(f"  Difference: ${abs(call_price - bs_price):.4f}")
    
    # Display tree parameters
    print(f"\nTree Parameters:")
    print(f"  Up factor (u): {call_pricer.u:.4f}")
    print(f"  Down factor (d): {call_pricer.d:.4f}")
    print(f"  Risk-neutral probability (p): {call_pricer.p:.4f}")
    
    # Show stock price tree sample
    stock_tree = call_pricer.build_stock_tree()
    call_pricer.display_tree_sample(stock_tree, "Stock Price")
    call_pricer.display_tree_sample(call_tree, "Call Option Value")
    
    # Example 2: American Put Option
    print("\n\n2. American Put Option")
    print("-" * 40)
    put_params = OptionParameters(
        S0=95,
        K=100,
        T=0.5,
        r=0.04,
        sigma=0.25,
        n=15,
        option_type='put',
        exercise_type='american'
    )
    
    put_pricer = SimpleBinomialTreePricer(put_params)
    put_price, _ = put_pricer.price_option()
    
    # Compare with European put
    put_params.exercise_type = 'european'
    european_put_pricer = SimpleBinomialTreePricer(put_params)
    european_put_price, _ = european_put_pricer.price_option()
    
    print(f"Parameters:")
    print(f"  Stock Price: ${put_params.S0}")
    print(f"  Strike Price: ${put_params.K}")
    print(f"  Time to Expiration: {put_params.T} years")
    print(f"  Risk-free Rate: {put_params.r:.1%}")
    print(f"  Volatility: {put_params.sigma:.1%}")
    
    print(f"\nResults:")
    print(f"  American Put Price: ${put_price:.4f}")
    print(f"  European Put Price: ${european_put_price:.4f}")
    print(f"  Early Exercise Premium: ${put_price - european_put_price:.4f}")
    
    # Example 3: Convergence demonstration
    print("\n\n3. Convergence Demonstration")
    print("-" * 40)
    convergence_params = OptionParameters(
        S0=100, K=100, T=0.25, r=0.05, sigma=0.2, n=10,
        option_type='call', exercise_type='european'
    )
    
    print("Steps\tBinomial Price")
    print("-" * 25)
    
    steps = [5, 10, 20, 50, 100]
    for n in steps:
        convergence_params.n = n
        pricer = SimpleBinomialTreePricer(convergence_params)
        price, _ = pricer.price_option()
        print(f"{n}\t${price:.4f}")
    
    bs_approx = black_scholes_simple(100, 100, 0.25, 0.05, 0.2, 'call')
    print(f"BS (approx)\t${bs_approx:.4f}")


def test_basic_functionality():
    """Test basic functionality of the simplified implementation"""
    print("\n" + "=" * 50)
    print("BASIC FUNCTIONALITY TESTS")
    print("=" * 50)
    
    # Test 1: Parameter validation
    print("\n1. Testing parameter validation...")
    try:
        # This should raise an error
        bad_params = OptionParameters(S0=-100, K=100, T=1, r=0.05, sigma=0.2, n=10, option_type='call')
        SimpleBinomialTreePricer(bad_params)
        print("❌ Parameter validation failed")
    except ValueError as e:
        print(f"✅ Parameter validation working: {e}")
    
    # Test 2: Basic pricing
    print("\n2. Testing basic option pricing...")
    test_params = OptionParameters(
        S0=100, K=100, T=1, r=0.05, sigma=0.2, n=20,
        option_type='call', exercise_type='european'
    )
    
    pricer = SimpleBinomialTreePricer(test_params)
    price, _ = pricer.price_option()
    
    if price > 0:
        print(f"✅ Basic pricing working: Call option price = ${price:.4f}")
    else:
        print("❌ Basic pricing failed")
    
    # Test 3: Put-call relationship
    print("\n3. Testing put-call relationship...")
    call_params = OptionParameters(S0=100, K=100, T=1, r=0.05, sigma=0.2, n=50, option_type='call', exercise_type='european')
    put_params = OptionParameters(S0=100, K=100, T=1, r=0.05, sigma=0.2, n=50, option_type='put', exercise_type='european')
    
    call_pricer = SimpleBinomialTreePricer(call_params)
    put_pricer = SimpleBinomialTreePricer(put_params)
    
    call_price, _ = call_pricer.price_option()
    put_price, _ = put_pricer.price_option()
    
    # Put-call parity: C - P = S - K*e^(-r*T)
    parity_left = call_price - put_price
    parity_right = 100 - 100 * math.exp(-0.05 * 1)
    
    if abs(parity_left - parity_right) < 0.1:
        print(f"✅ Put-call parity approximately satisfied")
        print(f"   C - P = {parity_left:.4f}, S - K*e^(-r*T) = {parity_right:.4f}")
    else:
        print(f"❌ Put-call parity not satisfied")
    
    # Test 4: American vs European put
    print("\n4. Testing American vs European put pricing...")
    american_params = OptionParameters(S0=90, K=100, T=1, r=0.05, sigma=0.3, n=30, option_type='put', exercise_type='american')
    european_params = OptionParameters(S0=90, K=100, T=1, r=0.05, sigma=0.3, n=30, option_type='put', exercise_type='european')
    
    american_pricer = SimpleBinomialTreePricer(american_params)
    european_pricer = SimpleBinomialTreePricer(european_params)
    
    american_price, _ = american_pricer.price_option()
    european_price, _ = european_pricer.price_option()
    
    if american_price >= european_price:
        print(f"✅ American put ≥ European put: ${american_price:.4f} ≥ ${european_price:.4f}")
    else:
        print(f"❌ American put < European put (this shouldn't happen)")


if __name__ == "__main__":
    # Run basic tests
    test_basic_functionality()
    
    # Run examples
    run_simple_examples()