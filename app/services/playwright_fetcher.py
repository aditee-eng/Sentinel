from playwright.async_api import async_playwright

PRICING_URLS = {
    "razorpay": "https://razorpay.com/pricing/",
    "cashfree": "https://www.cashfree.com/payment-gateway-charges/",
    "payu": "https://payu.in/pricing",
    "nextjs": "https://vercel.com/pricing",
    "supabase": "https://supabase.com/pricing",
}

async def get_pricing_data(competitor: str) -> list:
    url = PRICING_URLS.get(competitor)
    if not url:
        print(f"[{competitor}] No pricing URL configured, skipping.")
        return []

    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            context = await browser.new_context(
                user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                viewport={"width": 1280, "height": 720}
            )
            page = await context.new_page()
            await page.goto(url, timeout=30000)
            await page.wait_for_load_state("networkidle", timeout=15000)
            await page.wait_for_timeout(2000)

            pricing_elements = await page.evaluate("""
                () => {
                    const results = [];
                    const seen = new Set();
                    const allText = document.querySelectorAll('h1, h2, h3, h4, p, span');
                    
                    allText.forEach(el => {
                        const text = el.innerText?.trim();
                        
                        // skip empty, too long, already seen, or nav-like text
                        if (!text || text.length > 80 || text.length < 3) return;
                        if (seen.has(text)) return;
                        if (text.includes('\\n')) return;  // skip multi-line nav items
                        
                        const hasPricing = (
                            text.match(/[$][0-9]/) ||
                            text.match(/[0-9]+[/]mo/) ||
                            text.match(/free tier/i) ||
                            text.match(/per month/i) ||
                            text.match(/^(hobby|pro|starter|enterprise|team|free|basic|plus)$/i)
                        );
                        
                        if (hasPricing) {
                            seen.add(text);
                            results.push(text);
                        }
                    });
                    
                    return results.slice(0, 15);
                }
            """)

            await browser.close()

            return [
                f"[pricing] {competitor}: {item}"
                for item in pricing_elements
                if item.strip()
            ]

    except Exception as e:
        print(f"[{competitor}] Playwright error: {e}")
        return []