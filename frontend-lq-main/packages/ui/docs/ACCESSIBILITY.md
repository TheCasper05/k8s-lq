# Accessibility & Testing Guide

## Overview

This document outlines the accessibility features and testing attributes implemented across the `@lq/ui` component
library.

## Data Test IDs

All components now include `data-testid` attributes for automated testing. These can be customized via the `testId` prop
or will use sensible defaults.

### Usage

```vue
<!-- Custom test ID -->
<LqButton testId="submit-form-button">Submit</LqButton>

<!-- Default test ID: "lq-button-primary" -->
<LqButton variant="primary">Click Me</LqButton>
```

### Test ID Patterns

| Component | Default Pattern       | Example             |
| --------- | --------------------- | ------------------- |
| LqButton  | `lq-button-{variant}` | `lq-button-primary` |
| LqAvatar  | `lq-avatar`           | `lq-avatar`         |
| LqCard    | `lq-card-{variant}`   | `lq-card-default`   |
| LqModal   | `lq-modal`            | `lq-modal`          |
| LqHero    | `lq-hero-{variant}`   | `lq-hero-card`      |

## Accessibility Features

### ARIA Attributes

All interactive components include appropriate ARIA attributes:

#### LqButton

- `aria-label`: Custom label for screen readers
- `aria-busy`: Indicates loading state
- `aria-disabled`: Indicates disabled state
- `role="status"`: On loading spinner

```vue
<LqButton :loading="isSubmitting" ariaLabel="Submit registration form">
  Submit
</LqButton>
```

#### LqModal

- `role="dialog"`: Identifies as modal dialog
- `aria-modal="true"`: Indicates modal behavior
- `aria-labelledby`: Links to title element
- `aria-label`: Fallback when no title
- `aria-hidden="true"`: On backdrop element

```vue
<LqModal v-model="showModal" title="Confirm Action" ariaLabel="Confirmation dialog" />
```

#### LqAvatar

- `role="img"`: Identifies as image
- `aria-label`: Descriptive label
- `aria-hidden="true"`: On decorative icons

```vue
<LqAvatar src="/avatar.jpg" alt="User profile picture" />
```

#### LqCard

- `role="region"`: Identifies as landmark
- `aria-label`: Descriptive label for the card

```vue
<LqCard ariaLabel="User statistics card">
  <!-- content -->
</LqCard>
```

#### LqHero

- `<section>`: Semantic HTML element
- `aria-label`: Descriptive label for the section
- `aria-label="Go back"`: On back buttons
- `aria-hidden="true"`: On decorative icons

```vue
<LqHero variant="card" title="Activity Details" ariaLabel="Activity information section" />
```

### Keyboard Navigation

#### LqModal

- **ESC key**: Closes modal (when `closable=true`)
- **Focus trap**: Focus stays within modal when open
- **Tab navigation**: Proper tab order maintained

#### LqButton

- **Enter/Space**: Activates button
- **Tab**: Moves focus to/from button
- **Focus ring**: Visible focus indicator (`focus:ring-2`)

### Focus Management

All interactive components include visible focus indicators:

```css
/* Focus ring pattern used across components */
focus:outline-none focus:ring-2 focus:ring-primary-500
```

Components with focus management:

- ✅ LqButton
- ✅ LqModal (close button)
- ✅ LqHero (back button)
- ✅ All clickable elements

## Screen Reader Support

### Semantic HTML

Components use semantic HTML elements:

- `<button>` for interactive actions
- `<section>` for hero/card sections
- `<h1>`, `<h2>`, `<h3>` for headings
- `role` attributes where needed

### Hidden Content

Decorative elements are hidden from screen readers:

```vue
<!-- Icon is decorative, hidden from screen readers -->
<Icon name="solar:arrow-left-linear" aria-hidden="true" />

<!-- Text alternative provided -->
<span class="sr-only">Close</span>
```

### Loading States

Loading indicators include proper ARIA attributes:

```vue
<span v-if="loading" role="status" aria-label="Loading" class="spinner" />
```

## Testing Examples

### Unit Tests (Vitest)

```typescript
import { mount } from "@vue/test-utils";
import { LqButton } from "@lq/ui";

describe("LqButton", () => {
  it("renders with correct test id", () => {
    const wrapper = mount(LqButton, {
      props: { testId: "my-button" },
    });
    expect(wrapper.find('[data-testid="my-button"]').exists()).toBe(true);
  });

  it("shows loading state with aria-busy", async () => {
    const wrapper = mount(LqButton, {
      props: { loading: true },
    });
    expect(wrapper.attributes("aria-busy")).toBe("true");
  });

  it("has accessible label", () => {
    const wrapper = mount(LqButton, {
      props: { ariaLabel: "Submit form" },
    });
    expect(wrapper.attributes("aria-label")).toBe("Submit form");
  });
});
```

### E2E Tests (Playwright)

```typescript
import { test, expect } from "@playwright/test";

test("modal can be closed with ESC key", async ({ page }) => {
  await page.goto("/modal-example");

  // Open modal
  await page.click('[data-testid="open-modal-button"]');

  // Verify modal is visible
  await expect(page.locator('[data-testid="lq-modal"]')).toBeVisible();

  // Close with ESC
  await page.keyboard.press("Escape");

  // Verify modal is closed
  await expect(page.locator('[data-testid="lq-modal"]')).not.toBeVisible();
});

test("button is keyboard accessible", async ({ page }) => {
  await page.goto("/button-example");

  // Tab to button
  await page.keyboard.press("Tab");

  // Verify focus
  await expect(page.locator('[data-testid="lq-button-primary"]')).toBeFocused();

  // Activate with Enter
  await page.keyboard.press("Enter");

  // Verify action
  await expect(page.locator("#result")).toHaveText("Button clicked");
});
```

## Component-Specific Props

### LqButton

| Prop        | Type     | Default     | Description      |
| ----------- | -------- | ----------- | ---------------- |
| `testId`    | `string` | `undefined` | Custom test ID   |
| `ariaLabel` | `string` | `undefined` | Accessible label |

### LqAvatar

| Prop     | Type     | Default     | Description    |
| -------- | -------- | ----------- | -------------- |
| `testId` | `string` | `undefined` | Custom test ID |
| `alt`    | `string` | `undefined` | Image alt text |

### LqCard

| Prop        | Type     | Default     | Description      |
| ----------- | -------- | ----------- | ---------------- |
| `testId`    | `string` | `undefined` | Custom test ID   |
| `ariaLabel` | `string` | `undefined` | Card description |

### LqModal

| Prop        | Type     | Default     | Description                            |
| ----------- | -------- | ----------- | -------------------------------------- |
| `testId`    | `string` | `undefined` | Custom test ID                         |
| `ariaLabel` | `string` | `undefined` | Modal description                      |
| `title`     | `string` | `undefined` | Modal title (used for aria-labelledby) |

### LqHero

| Prop        | Type     | Default     | Description         |
| ----------- | -------- | ----------- | ------------------- |
| `testId`    | `string` | `undefined` | Custom test ID      |
| `ariaLabel` | `string` | `undefined` | Section description |

## Best Practices

### 1. Always Provide Meaningful Labels

```vue
<!-- ❌ Bad: No context -->
<LqButton>Submit</LqButton>

<!-- ✅ Good: Clear context -->
<LqButton ariaLabel="Submit registration form">Submit</LqButton>
```

### 2. Use Semantic HTML

```vue
<!-- ❌ Bad: Generic div -->
<div class="hero">...</div>

<!-- ✅ Good: Semantic section -->
<LqHero variant="card">...</LqHero>
```

### 3. Hide Decorative Elements

```vue
<!-- ❌ Bad: Icon announced by screen reader -->
<Icon name="check" />

<!-- ✅ Good: Icon hidden, text alternative provided -->
<Icon name="check" aria-hidden="true" />
<span class="sr-only">Success</span>
```

### 4. Provide Loading Feedback

```vue
<!-- ✅ Good: Loading state is accessible -->
<LqButton :loading="isLoading" ariaLabel="Saving changes">
  Save
</LqButton>
```

### 5. Use Consistent Test IDs

```vue
<!-- ✅ Good: Descriptive, unique test IDs -->
<LqButton testId="submit-registration-form">Submit</LqButton>
<LqButton testId="cancel-registration-form">Cancel</LqButton>
```

## Accessibility Checklist

When creating new components or features:

- [ ] Add `data-testid` attribute
- [ ] Include appropriate ARIA attributes
- [ ] Ensure keyboard navigation works
- [ ] Add visible focus indicators
- [ ] Use semantic HTML elements
- [ ] Hide decorative elements from screen readers
- [ ] Provide text alternatives for images/icons
- [ ] Test with screen reader (NVDA/JAWS/VoiceOver)
- [ ] Test keyboard-only navigation
- [ ] Verify color contrast (WCAG AA minimum)

## Resources

- [WAI-ARIA Authoring Practices](https://www.w3.org/WAI/ARIA/apg/)
- [WebAIM Accessibility Guidelines](https://webaim.org/standards/wcag/checklist)
- [MDN Accessibility](https://developer.mozilla.org/en-US/docs/Web/Accessibility)
- [Testing Library Best Practices](https://testing-library.com/docs/queries/about#priority)

## Support

For questions or issues related to accessibility:

1. Check this documentation
2. Review component source code
3. Create an issue in the repository
4. Contact the UI team

---

**Last Updated**: December 2025 **Maintained By**: LingoQuesto UI Team
