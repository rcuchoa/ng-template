# Options Pricing with Binomial Trees

This repository contains a comprehensive implementation of the binomial tree model for options pricing, supporting both European and American options.

## Files Overview

### Core Implementation Files

1. **`options_pricing.py`** - Full-featured implementation with NumPy/SciPy
   - Supports Greeks calculation
   - Includes Black-Scholes comparison
   - Comprehensive error handling
   - Advanced features

2. **`simple_options_pricing.py`** - Standalone implementation using only built-in libraries
   - No external dependencies
   - Basic functionality demonstration
   - Easy to understand and modify

3. **`test_options_pricing.py`** - Comprehensive test suite
   - Unit tests for validation
   - Performance tests
   - Put-call parity verification

4. **`requirements.txt`** - Python dependencies for full implementation

## Quick Start

### Using the Simplified Version (No Dependencies)

```python
from simple_options_pricing import SimpleBinomialTreePricer, OptionParameters

# Define option parameters
params = OptionParameters(
    S0=100,          # Current stock price
    K=105,           # Strike price
    T=0.25,          # Time to expiration (years)
    r=0.05,          # Risk-free rate
    sigma=0.2,       # Volatility
    n=50,            # Number of time steps
    option_type='call',
    exercise_type='european'
)

# Create pricer and calculate option price
pricer = SimpleBinomialTreePricer(params)
price, option_tree = pricer.price_option()

print(f"Option Price: ${price:.4f}")
```

### Using the Full Implementation (With NumPy/SciPy)

```python
from options_pricing import BinomialTreePricer, OptionParameters

# Define parameters (same as above)
params = OptionParameters(...)

# Create pricer
pricer = BinomialTreePricer(params)

# Calculate option price
price, option_tree = pricer.price_option()

# Calculate Greeks
greeks = pricer.calculate_greeks()

print(f"Option Price: ${price:.4f}")
print(f"Delta: {greeks['delta']:.4f}")
print(f"Gamma: {greeks['gamma']:.4f}")
print(f"Theta: {greeks['theta']:.4f}")
print(f"Vega: {greeks['vega']:.4f}")
print(f"Rho: {greeks['rho']:.4f}")
```

## Parameter Explanation

| Parameter | Description | Example |
|-----------|-------------|---------|
| `S0` | Current stock price | 100.0 |
| `K` | Strike price | 105.0 |
| `T` | Time to expiration (years) | 0.25 (3 months) |
| `r` | Risk-free interest rate | 0.05 (5%) |
| `sigma` | Volatility (annualized) | 0.2 (20%) |
| `n` | Number of time steps | 50-100 |
| `option_type` | 'call' or 'put' | 'call' |
| `exercise_type` | 'european' or 'american' | 'european' |

## Binomial Tree Model

The implementation uses the Cox-Ross-Rubinstein (CRR) binomial tree model:

### Tree Parameters
- **Up factor**: `u = exp(σ√Δt)`
- **Down factor**: `d = 1/u`
- **Risk-neutral probability**: `p = (exp(rΔt) - d) / (u - d)`
- **Time step**: `Δt = T/n`

### Algorithm Steps
1. Build stock price tree using up/down factors
2. Calculate option payoffs at expiration
3. Work backwards through tree using risk-neutral valuation
4. For American options, check early exercise at each node

## Examples

### European Call Option
```python
# At-the-money call option
call_params = OptionParameters(
    S0=100, K=100, T=0.25, r=0.05, sigma=0.2, n=100,
    option_type='call', exercise_type='european'
)

pricer = SimpleBinomialTreePricer(call_params)
price, _ = pricer.price_option()
# Expected result: ~$4.60
```

### American Put Option
```python
# In-the-money put option
put_params = OptionParameters(
    S0=90, K=100, T=0.5, r=0.05, sigma=0.3, n=100,
    option_type='put', exercise_type='american'
)

pricer = SimpleBinomialTreePricer(put_params)
american_price, _ = pricer.price_option()

# Compare with European put
put_params.exercise_type = 'european'
european_pricer = SimpleBinomialTreePricer(put_params)
european_price, _ = european_pricer.price_option()

early_exercise_premium = american_price - european_price
```

## Key Features

### 1. Validation
- All parameters are validated for reasonable values
- Risk-neutral probability checked for convergence conditions

### 2. Convergence
- As number of steps increases, binomial tree converges to Black-Scholes
- Recommended: n ≥ 50 for reasonable accuracy

### 3. Early Exercise
- American options properly handle early exercise decisions
- Early exercise premium automatically calculated

### 4. Greeks (Full Implementation Only)
- Delta: Price sensitivity to stock price
- Gamma: Delta sensitivity to stock price  
- Theta: Price sensitivity to time decay
- Vega: Price sensitivity to volatility
- Rho: Price sensitivity to interest rate

## Testing

Run the test suite to verify implementation:

```bash
# Test simplified version
python3 simple_options_pricing.py

# Test full version (requires NumPy/SciPy)
python3 test_options_pricing.py
```

## Installation

### For Simple Version
No installation required - uses only Python built-ins.

### For Full Version
```bash
pip install -r requirements.txt
```

Or install manually:
```bash
pip install numpy scipy matplotlib
```

## Mathematical Background

### Put-Call Parity
For European options: `C - P = S - K*e^(-rT)`

Where:
- C = Call option price
- P = Put option price  
- S = Current stock price
- K = Strike price
- r = Risk-free rate
- T = Time to expiration

### Black-Scholes Comparison
The binomial tree model converges to the Black-Scholes model as the number of steps approaches infinity. The full implementation includes a Black-Scholes calculator for comparison.

## Performance Considerations

- **Time Complexity**: O(n²) where n is the number of steps
- **Space Complexity**: O(n²) for storing the complete tree
- **Accuracy**: Generally converges well with n ≥ 50
- **American Options**: Slightly more expensive due to early exercise checks

## Limitations

1. Assumes constant volatility and risk-free rate
2. No dividends in current implementation
3. European-style early exercise rules for American options
4. Single underlying asset only

## Extension Ideas

1. **Dividend Support**: Add discrete or continuous dividend yields
2. **Barrier Options**: Implement knock-in/knock-out features
3. **Asian Options**: Path-dependent payoffs
4. **Multi-asset**: Extend to basket options
5. **Stochastic Volatility**: Incorporate volatility models

## References

- Cox, J. C., Ross, S. A., & Rubinstein, M. (1979). "Option pricing: A simplified approach"
- Hull, J. C. "Options, Futures, and Other Derivatives"
- Wilmott, P. "Paul Wilmott Introduces Quantitative Finance"