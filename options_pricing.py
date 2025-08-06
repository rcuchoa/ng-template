import numpy as np
import math
from typing import Literal, Tuple, Optional
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


class BinomialTreePricer:
    """
    Binomial Tree Options Pricing Calculator
    
    This class implements the Cox-Ross-Rubinstein (CRR) binomial tree model
    for pricing both European and American options.
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
    
    def build_stock_tree(self) -> np.ndarray:
        """
        Build the stock price tree
        
        Returns:
            2D numpy array containing stock prices at each node
        """
        n = self.params.n
        stock_tree = np.zeros((n + 1, n + 1))
        
        for i in range(n + 1):
            for j in range(i + 1):
                stock_tree[j, i] = self.params.S0 * (self.u ** (i - j)) * (self.d ** j)
        
        return stock_tree
    
    def price_option(self) -> Tuple[float, np.ndarray]:
        """
        Price the option using binomial tree method
        
        Returns:
            Tuple of (option_price, option_tree)
        """
        n = self.params.n
        
        # Build stock price tree
        stock_tree = self.build_stock_tree()
        
        # Initialize option value tree
        option_tree = np.zeros((n + 1, n + 1))
        
        # Calculate option values at expiration (final column)
        for j in range(n + 1):
            option_tree[j, n] = self._payoff(stock_tree[j, n])
        
        # Work backwards through the tree
        for i in range(n - 1, -1, -1):
            for j in range(i + 1):
                # Calculate expected option value
                expected_value = self.discount_factor * (
                    self.p * option_tree[j, i + 1] + 
                    (1 - self.p) * option_tree[j + 1, i + 1]
                )
                
                if self.params.exercise_type == 'american':
                    # For American options, check early exercise
                    early_exercise = self._early_exercise_value(stock_tree[j, i])
                    option_tree[j, i] = max(expected_value, early_exercise)
                else:
                    # For European options, no early exercise
                    option_tree[j, i] = expected_value
        
        return option_tree[0, 0], option_tree
    
    def calculate_greeks(self) -> dict:
        """
        Calculate option Greeks using finite difference methods
        
        Returns:
            Dictionary containing Delta, Gamma, Theta, Vega, and Rho
        """
        original_price, _ = self.price_option()
        
        # Delta: sensitivity to stock price
        ds = 0.01 * self.params.S0
        self.params.S0 += ds
        price_up, _ = self.price_option()
        self.params.S0 -= 2 * ds
        price_down, _ = self.price_option()
        self.params.S0 += ds  # Reset to original
        
        delta = (price_up - price_down) / (2 * ds)
        gamma = (price_up - 2 * original_price + price_down) / (ds ** 2)
        
        # Theta: sensitivity to time
        dt = 1/365  # 1 day
        if self.params.T > dt:
            original_T = self.params.T
            self.params.T -= dt
            self.dt = self.params.T / self.params.n
            self._recalculate_tree_params()
            price_theta, _ = self.price_option()
            self.params.T = original_T  # Reset
            self.dt = self.params.T / self.params.n
            self._recalculate_tree_params()
            theta = price_theta - original_price
        else:
            theta = 0
        
        # Vega: sensitivity to volatility
        dvol = 0.01
        self.params.sigma += dvol
        self._recalculate_tree_params()
        price_vega, _ = self.price_option()
        self.params.sigma -= dvol  # Reset
        self._recalculate_tree_params()
        
        vega = price_vega - original_price
        
        # Rho: sensitivity to risk-free rate
        dr = 0.01
        self.params.r += dr
        self._recalculate_tree_params()
        price_rho, _ = self.price_option()
        self.params.r -= dr  # Reset
        self._recalculate_tree_params()
        
        rho = price_rho - original_price
        
        return {
            'delta': delta,
            'gamma': gamma,
            'theta': theta,
            'vega': vega,
            'rho': rho
        }
    
    def _recalculate_tree_params(self):
        """Recalculate tree parameters after parameter changes"""
        self.u = math.exp(self.params.sigma * math.sqrt(self.dt))
        self.d = 1 / self.u
        self.p = (math.exp(self.params.r * self.dt) - self.d) / (self.u - self.d)
        self.discount_factor = math.exp(-self.params.r * self.dt)


def black_scholes_comparison(params: OptionParameters) -> float:
    """
    Calculate Black-Scholes price for comparison (European options only)
    
    Args:
        params: Option parameters
        
    Returns:
        Black-Scholes option price
    """
    from scipy.stats import norm
    
    if params.exercise_type != 'european':
        raise ValueError("Black-Scholes is only applicable to European options")
    
    S, K, T, r, sigma = params.S0, params.K, params.T, params.r, params.sigma
    
    d1 = (math.log(S/K) + (r + 0.5 * sigma**2) * T) / (sigma * math.sqrt(T))
    d2 = d1 - sigma * math.sqrt(T)
    
    if params.option_type == 'call':
        price = S * norm.cdf(d1) - K * math.exp(-r * T) * norm.cdf(d2)
    else:  # put
        price = K * math.exp(-r * T) * norm.cdf(-d2) - S * norm.cdf(-d1)
    
    return price


# Example usage and testing
if __name__ == "__main__":
    # Example 1: European Call Option
    print("=== European Call Option ===")
    call_params = OptionParameters(
        S0=100,          # Current stock price
        K=105,           # Strike price
        T=0.25,          # 3 months to expiration
        r=0.05,          # 5% risk-free rate
        sigma=0.2,       # 20% volatility
        n=50,            # 50 time steps
        option_type='call',
        exercise_type='european'
    )
    
    call_pricer = BinomialTreePricer(call_params)
    call_price, call_tree = call_pricer.price_option()
    call_greeks = call_pricer.calculate_greeks()
    
    print(f"Binomial Tree Price: ${call_price:.4f}")
    
    try:
        bs_price = black_scholes_comparison(call_params)
        print(f"Black-Scholes Price: ${bs_price:.4f}")
        print(f"Difference: ${abs(call_price - bs_price):.4f}")
    except ImportError:
        print("SciPy not available for Black-Scholes comparison")
    
    print("\nGreeks:")
    for greek, value in call_greeks.items():
        print(f"  {greek.capitalize()}: {value:.4f}")
    
    # Example 2: American Put Option
    print("\n=== American Put Option ===")
    put_params = OptionParameters(
        S0=100,
        K=105,
        T=0.25,
        r=0.05,
        sigma=0.2,
        n=50,
        option_type='put',
        exercise_type='american'
    )
    
    put_pricer = BinomialTreePricer(put_params)
    put_price, put_tree = put_pricer.price_option()
    put_greeks = put_pricer.calculate_greeks()
    
    print(f"American Put Price: ${put_price:.4f}")
    
    # Compare with European put
    put_params.exercise_type = 'european'
    european_put_pricer = BinomialTreePricer(put_params)
    european_put_price, _ = european_put_pricer.price_option()
    
    print(f"European Put Price: ${european_put_price:.4f}")
    print(f"Early Exercise Premium: ${put_price - european_put_price:.4f}")
    
    print("\nGreeks:")
    for greek, value in put_greeks.items():
        print(f"  {greek.capitalize()}: {value:.4f}")