// Import necessary functions from Vitest, the testing framework.
import { describe, it, expect, beforeEach, afterEach } from "vitest";

// A 'describe' block groups related tests. It's a good practice to have one main
// 'describe' per file, named after the module or component being tested.
describe("ExampleTestSuite", () => {
  // 'beforeEach' runs a function before each of the tests in this 'describe' block.
  // It's useful for setting up a clean state for each test.
  beforeEach(() => {
    // For example, you could reset a mock database or component state here.
    console.log("Setting up for a new test...");
  });

  // 'afterEach' runs a function after each of the tests in this 'describe' block.
  // It's useful for cleaning up after a test has run.
  afterEach(() => {
    // For example, you could clean up any resources used in the test.
    console.log("Cleaning up after a test...");
  });

  // You can nest 'describe' blocks to group tests for a specific function or feature.
  describe("featureOrFunctionToTest", () => {
    // An 'it' or 'test' block defines an individual test case.
    // The description should clearly state what the test is verifying.
    it("should behave correctly under specific conditions", () => {
      // Arrange: Set up the variables and conditions for your test.
      const a = 1;
      const b = 2;
      let result = 0;

      // Act: Execute the code you want to test.
      result = a + b;

      // Assert: Check if the result is what you expect.
      // 'expect' is used to create an assertion. It's paired with a "matcher" function (e.g., .toBe(), .toEqual()).
      expect(result).toBe(3);
    });

    it("should handle another case", () => {
      // Example of another test case.
      const text = "hello world";
      expect(text).toContain("hello");
    });
  });

  // Another group of tests.
  describe("anotherFeature", () => {
    it("should return true for a simple case", () => {
      expect(true).toBe(true);
    });
  });
});
