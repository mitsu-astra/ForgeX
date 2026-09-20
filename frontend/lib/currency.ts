/**
 * Currency utility for ForgeX • Industrial Decision Intelligence Platform
 * Standardizes financial and cost metrics in Indian Rupees (INR, ₹).
 */

// Baseline benchmark conversion rate: 1 USD = ₹83.50 INR
export const USD_TO_INR_RATE = 83.5;

/**
 * Converts a USD value to INR and formats with the ₹ symbol and Indian numbering system (Lakhs / Crores).
 */
export function formatINR(
  usdAmount: number | null | undefined,
  options: { compact?: boolean } = {}
): string {
  if (usdAmount == null || isNaN(usdAmount)) return "₹0";
  const inrValue = usdAmount * USD_TO_INR_RATE;

  if (options.compact) {
    if (Math.abs(inrValue) >= 10000000) {
      return `₹${(inrValue / 10000000).toFixed(2)} Cr`;
    }
    if (Math.abs(inrValue) >= 100000) {
      return `₹${(inrValue / 100000).toFixed(2)} Lakhs`;
    }
    if (Math.abs(inrValue) >= 1000) {
      return `₹${(inrValue / 1000).toFixed(1)}K`;
    }
    return `₹${Math.round(inrValue).toLocaleString("en-IN")}`;
  }

  return `₹${Math.round(inrValue).toLocaleString("en-IN")}`;
}

/**
 * Formats a value already in INR.
 */
export function formatINRDirect(
  inrAmount: number | null | undefined,
  compact = false
): string {
  if (inrAmount == null || isNaN(inrAmount)) return "₹0";

  if (compact) {
    if (Math.abs(inrAmount) >= 10000000) {
      return `₹${(inrAmount / 10000000).toFixed(2)} Cr`;
    }
    if (Math.abs(inrAmount) >= 100000) {
      return `₹${(inrAmount / 100000).toFixed(2)} Lakhs`;
    }
    if (Math.abs(inrAmount) >= 1000) {
      return `₹${(inrAmount / 1000).toFixed(1)}K`;
    }
  }

  return `₹${Math.round(inrAmount).toLocaleString("en-IN")}`;
}
