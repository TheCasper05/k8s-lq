import { describe, it, expect, vi, type Mock } from "vitest";
import { mount } from "@vue/test-utils";
import AppBreadcrumb from "~/components/AppBreadcrumb.vue";
import { useRoute } from "vue-router";

// Mock vue-router
vi.mock("vue-router", () => ({
  useRoute: vi.fn(),
}));

// Stub NuxtLink
const NuxtLinkStub = {
  props: ["to"],
  template: '<a :href="to"><slot /></a>',
};

// Stub Icon
const IconStub = {
  name: "Icon",
  template: "<span></span>",
};

describe("AppBreadcrumb", () => {
  it("renders default dashboard breadcrumb when path is root", () => {
    (useRoute as Mock).mockReturnValue({ path: "/" });

    const wrapper = mount(AppBreadcrumb, {
      global: {
        components: {
          NuxtLink: NuxtLinkStub,
          Icon: IconStub,
        },
      },
    });

    const crumbs = wrapper.findAll("li");
    expect(crumbs.length).toBe(1);
    expect(crumbs[0].text()).toContain("Dashboard");
  });

  it("renders correct breadcrumbs for a nested route", () => {
    (useRoute as Mock).mockReturnValue({ path: "/student/courses" });

    const wrapper = mount(AppBreadcrumb, {
      global: {
        components: {
          NuxtLink: NuxtLinkStub,
          Icon: IconStub,
        },
      },
    });

    const crumbs = wrapper.findAll("li");
    expect(crumbs.length).toBe(2);

    expect(crumbs[0].text()).toContain("Student");
    expect(crumbs[1].text()).toContain("Courses");
  });

  it("capitalizes and formats labels correctly", () => {
    (useRoute as Mock).mockReturnValue({ path: "/my-assignments/detail" });

    const wrapper = mount(AppBreadcrumb, {
      global: {
        components: {
          NuxtLink: NuxtLinkStub,
          Icon: IconStub,
        },
      },
    });

    const crumbs = wrapper.findAll("li");
    expect(crumbs[0].text()).toContain("My assignments");
    expect(crumbs[1].text()).toContain("Detail");
  });

  it("marks the last crumb as active (no link)", () => {
    (useRoute as Mock).mockReturnValue({ path: "/student/profile" });

    const wrapper = mount(AppBreadcrumb, {
      global: {
        components: {
          NuxtLink: NuxtLinkStub,
          Icon: IconStub,
        },
      },
    });

    const crumbs = wrapper.findAll("li");
    const lastCrumb = crumbs[crumbs.length - 1];

    // Last crumb should be a span, not a NuxtLink (which is mocked as 'a')
    expect(lastCrumb.find("a").exists()).toBe(false);
    expect(lastCrumb.find("span[aria-current='page']").exists()).toBe(true);
  });

  it("renders separators between items", () => {
    (useRoute as Mock).mockReturnValue({ path: "/a/b/c" });

    const wrapper = mount(AppBreadcrumb, {
      global: {
        components: {
          NuxtLink: NuxtLinkStub,
          Icon: IconStub,
        },
      },
    });

    // Should have 2 separators for 3 items
    const separators = wrapper.findAll("span.text-surface-400");
    // Note: The logic in the component uses v-if="index > 0" for separators.
    // Index 0: No separator
    // Index 1: Separator
    // Index 2: Separator
    // Total separators = 2
    expect(separators.length).toBe(2);
    expect(separators[0].text()).toBe("/");
  });
});
