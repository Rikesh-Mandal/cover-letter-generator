"use client";

import { useState } from "react";

export default function Home() {
  const [jobUrl, setJobUrl] = useState("");
  const [cvFile, setCvFile] = useState<File | null>(null);
  const [coverLetter, setCoverLetter] = useState("");
  const [loading, setLoading] = useState(false);

  async function handleGenerate() {
    if (!cvFile || !jobUrl.trim()) {
      return;
    }

    setLoading(true);
    setCoverLetter("");

    try {
      const formData = new FormData();

      formData.append("cv", cvFile);
      formData.append("job_url", jobUrl);

      const response = await fetch(
        "http://127.0.0.1:8000/generate",
        {
          method: "POST",
          body: formData,
        }
      );

      if (!response.ok) {
        throw new Error(
          "Failed to generate cover letter."
        );
      }

      if (!response.body) {
        throw new Error(
          "The server returned no response stream."
        );
      }

      const textStream = response.body.pipeThrough(
        new TextDecoderStream()
      );

      const reader = textStream.getReader();

      while (true) {
        const { value, done } = await reader.read();

        if (done) {
          break;
        }

        setCoverLetter(
          (currentText) => currentText + value
        );
      }
    } catch (error) {
      console.error(error);

      setCoverLetter(
        "Something went wrong while generating the cover letter."
      );
    } finally {
      setLoading(false);
    }
  }

  async function handleDownloadPdf() {
    if (!coverLetter) {
      return;
    }

    try {
      const response = await fetch(
        "http://127.0.0.1:8000/download-pdf",
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            cover_letter: coverLetter,
          }),
        }
      );

      if (!response.ok) {
        throw new Error(
          "Failed to create PDF."
        );
      }

      const pdfBlob = await response.blob();

      const url = URL.createObjectURL(pdfBlob);

      const link = document.createElement("a");

      link.href = url;
      link.download = "cover-letter.pdf";

      document.body.appendChild(link);

      link.click();

      link.remove();

      URL.revokeObjectURL(url);
    } catch (error) {
      console.error(
        "PDF download failed:",
        error
      );
    }
  }

  return (
    <main className="h-screen overflow-hidden bg-gray-50 px-6 py-6">
      <div className="mx-auto flex h-full max-w-7xl flex-col">

        {/* Header */}
        <header className="mb-6 text-center">
          <h1 className="text-4xl font-bold text-gray-900">
            AI Cover Letter Generator
          </h1>

          <p className="mt-2 text-gray-600">
            Upload your CV and provide a job posting URL to generate
            a tailored cover letter.
          </p>
        </header>

        {/* Main workspace */}
        <div className="grid min-h-0 flex-1 grid-cols-1 gap-6 lg:grid-cols-[360px_1fr]">

          {/* Left panel */}
          <section className="h-fit rounded-xl bg-white p-6 shadow-sm">

            <h2 className="mb-6 text-xl font-semibold text-gray-900">
              Job Details
            </h2>

            {/* CV upload */}
            <div className="mb-6">
              <label
                htmlFor="cv"
                className="mb-2 block font-medium text-gray-800"
              >
                Upload CV
              </label>

              <input
                id="cv"
                type="file"
                accept=".pdf"
                onChange={(e) => {
                  const file =
                    e.currentTarget.files?.[0] ?? null;

                  setCvFile(file);
                }}
                className="w-full rounded-lg border border-gray-300 p-3"
              />

              {cvFile && (
                <p className="mt-2 truncate text-sm text-gray-600">
                  Selected: {cvFile.name}
                </p>
              )}
            </div>

            {/* Job URL */}
            <div className="mb-6">
              <label
                htmlFor="job-url"
                className="mb-2 block font-medium text-gray-800"
              >
                Job posting URL
              </label>

              <input
                id="job-url"
                type="url"
                value={jobUrl}
                onChange={(e) =>
                  setJobUrl(e.currentTarget.value)
                }
                placeholder="https://company.com/jobs/..."
                className="w-full rounded-lg border border-gray-300 p-3"
              />
            </div>

            {/* Generate button */}
            <button
              type="button"
              onClick={handleGenerate}
              disabled={loading}
              className="w-full rounded-lg bg-black px-4 py-3 font-medium text-white disabled:cursor-not-allowed disabled:opacity-50"
            >
              {loading
                ? "Generating..."
                : "Generate Cover Letter"}
            </button>

          </section>

          {/* Right panel */}
          <section className="flex min-h-0 flex-col overflow-hidden rounded-xl bg-white shadow-sm">

            {/* Fixed result header */}
            <div className="border-b border-gray-200 px-6 py-4">

              <h2 className="text-xl font-semibold text-gray-900">
                Generated Cover Letter
              </h2>

            </div>

            {/* Scrollable result */}
            <div className="min-h-0 flex-1 overflow-y-auto p-6">

              <div className="whitespace-pre-wrap leading-7 text-gray-700">
                {coverLetter ||
                  "Your generated cover letter will appear here."}
              </div>

            </div>

            {/* Fixed download section */}
            {coverLetter && !loading && (
              <div className="border-t border-gray-200 px-6 py-4">

                <button
                  type="button"
                  onClick={handleDownloadPdf}
                  className="rounded-lg bg-black px-5 py-3 font-medium text-white"
                >
                  Download as PDF
                </button>

              </div>
            )}

          </section>

        </div>

      </div>
    </main>
  );
}