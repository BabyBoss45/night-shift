import { describe, expect, it } from "vitest";
import { ICONS, PICTOGRAMS, pictogramFor } from "./icons";

describe("pixel icons", () => {
  it("draws every icon on a full 12 by 12 grid", () => {
    for (const [name, rows] of Object.entries(ICONS)) {
      expect(rows.length, name).toBe(12);
      for (const row of rows) expect(row.length, `${name}: "${row}"`).toBe(12);
    }
  });

  it("draws every document pictogram on a full 16 by 16 grid", () => {
    for (const [name, rows] of Object.entries(PICTOGRAMS)) {
      expect(rows.length, name).toBe(16);
      for (const row of rows) expect(row.length, `${name}: "${row}"`).toBe(16);
    }
  });

  it("picks a pictogram from the sample's file name", () => {
    expect(pictogramFor("01_tenancy_agreement.pdf")).toBe(PICTOGRAMS.tenancy);
    expect(pictogramFor("05_nda.pdf")).toBe(PICTOGRAMS.nda);
    expect(pictogramFor("19_payslip.pdf")).toBe(PICTOGRAMS.coin);
    expect(pictogramFor("27_cv.pdf")).toBe(PICTOGRAMS.person);
    expect(pictogramFor("09_quarterly_report.pdf")).toBe(PICTOGRAMS.file);
  });
});
