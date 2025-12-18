import { describe, it, expect } from "vitest";
import { mount } from "@vue/test-utils";
import { LqButton } from "@lq/ui";

describe("LqButton", () => {
  it("renders with default props", () => {
    const wrapper = mount(LqButton, {
      slots: {
        default: "Click me",
      },
    });

    expect(wrapper.text()).toBe("Click me");
    expect(wrapper.find("button").exists()).toBe(true);
  });

  it("applies variant classes", () => {
    const wrapper = mount(LqButton, {
      props: {
        variant: "primary",
      },
    });

    expect(wrapper.find("button").classes()).toContain("bg-primary-600");
  });

  it("emits click event", async () => {
    const wrapper = mount(LqButton, {
      slots: {
        default: "Click me",
      },
    });

    await wrapper.find("button").trigger("click");

    expect(wrapper.emitted("click")).toBeTruthy();
    expect(wrapper.emitted("click")?.length).toBe(1);
  });

  it("does not emit click when disabled", async () => {
    const wrapper = mount(LqButton, {
      props: {
        disabled: true,
      },
      slots: {
        default: "Click me",
      },
    });

    await wrapper.find("button").trigger("click");

    expect(wrapper.emitted("click")).toBeFalsy();
  });

  it("shows loading spinner", () => {
    const wrapper = mount(LqButton, {
      props: {
        loading: true,
      },
      slots: {
        default: "Click me",
      },
    });

    expect(wrapper.find(".animate-spin").exists()).toBe(true);
  });
});
