import PreviousButton from "@/components/datepicker/PreviousButton";

async function createEvent(formData) {
  const response = await fetch("/api/event/create", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(formData),
  });

  if (!response.ok) {
    throw new Error("Failed to create event");
  }

  return response.json();
}

export default function ReviewSubmit({ data, prevComponent, isOwner }) {
  const handleSubmit = async () => {
    // Handle form submission logic here
    const formData = {
      ...data,
      start: data.start?.toISOString() || "",
      end: data.end?.toISOString() || "",
    };

    const result = await createEvent(formData);
    if (tg) {
      tg.close();
    }
  };

  const formatDate = (dateValue) => {
    if (!dateValue) return "Not selected";
    try {
      if (typeof dateValue === "string") return dateValue;
      if (dateValue.toString) return dateValue.toString();
      return String(dateValue);
    } catch (error) {
      console.warn("Error formatting date:", error);
      return "Invalid date";
    }
  };

  return (
    <div
      className="relative w-full max-w-md mx-auto font-body"
      data-testid="summary"
    >
      {/* Animated Background */}
      <div className="mb-16 relative">
        {/* Floating Sprites Animation */}
        <div className="absolute inset-0 overflow-hidden pointer-events-none">
          <div className="absolute top-4 left-4 w-2 h-2 bg-[#e5e5e5] animate-pulse"></div>
          <div
            className="absolute top-8 right-6 w-1 h-1 bg-[#c44545] animate-bounce"
            style={{ animationDelay: "0.5s" }}
          ></div>
          <div
            className="absolute bottom-12 left-8 w-1 h-1 bg-white animate-ping"
            style={{ animationDelay: "1s" }}
          ></div>
          <div
            className="absolute top-16 right-12 w-2 h-2 bg-[#8c2e2e] animate-pulse"
            style={{ animationDelay: "1.5s" }}
          ></div>
        </div>

        {/* Mobile Game UI Card */}
        <div
          className="relative bg-gradient-to-b from-[#2a2a2a] via-[#1a1a1a] to-[#0a0a0a] border-4 border-[#8c2e2e] shadow-2xl font-body rounded-lg overflow-hidden"
          style={{
            background: "linear-gradient(to bottom, #2a2a2a, #1a1a1a, #0a0a0a)",
            boxShadow:
              "0 0 20px rgba(196, 69, 69, 0.3), inset 0 2px 4px rgba(140, 46, 46, 0.2)",
          }}
        >
          {/* Decorative Header Border */}
          <div className="h-2 bg-gradient-to-r from-[#8c2e2e] via-[#c44545] to-[#8c2e2e]"></div>

          {/* Event Title - Game Style */}
          <div className="px-6 py-4 text-center border-b-2 border-[#8c2e2e] relative font-body">
            {/* Side Sprites */}
            <span className="absolute left-4 top-1/2 transform -translate-y-1/2 text-xl animate-bounce">
              🎉
            </span>
            <span
              className="absolute right-4 top-1/2 transform -translate-y-1/2 text-xl animate-bounce"
              style={{ animationDelay: "0.3s" }}
            >
              🎉
            </span>

            <h2 className="text-2xl font-bold text-white font-heading leading-tight">
              {data.event_name || "Awesome Event"}
            </h2>
          </div>

          {/* Content Layout */}
          <div className="p-6 font-body">
            {/* Description - Full Width */}
            <div className="mb-4 p-3 bg-gradient-to-r from-[#2a2a2a]/50 to-[#1a1a1a]/50 border border-[#8c2e2e]/50 font-body">
              <div className="flex items-start space-x-2">
                <span className="text-[#c44545] text-lg mt-1">💬</span>
                <div className="flex-1">
                  <div className="text-[#c44545] font-ui text-xs font-bold mb-1">
                    Description
                  </div>
                  <div className="text-[#e5e5e5] font-body text-sm leading-relaxed">
                    {data.event_details || "No description provided"}
                  </div>
                </div>
              </div>
            </div>

            {/* Date Pills - Side by Side */}
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
              {/* Start Date Pill */}
              <div className="p-3 bg-gradient-to-r from-[#8c2e2e]/30 to-[#c44545]/30 border border-[#8c2e2e] font-body">
                <div className="text-center">
                  <div className="flex justify-center items-center space-x-1 mb-1">
                    <span className="text-lg">🌟</span>
                    <span className="text-[#c44545] font-ui text-xs font-bold">
                      EARLIEST FROM
                    </span>
                  </div>
                  <div className="text-white font-body text-sm font-bold">
                    {formatDate(data.start)}
                  </div>
                </div>
              </div>

              {/* End Date Pill */}
              <div className="p-3 bg-gradient-to-r from-[#c44545]/30 to-[#8c2e2e]/30 border border-[#8c2e2e] font-body">
                <div className="text-center">
                  <div className="flex justify-center items-center space-x-1 mb-1">
                    <span className="text-lg">🎯</span>
                    <span className="text-[#c44545] font-ui text-xs font-bold">
                      LATEST BY
                    </span>
                  </div>
                  <div className="text-white font-body text-sm font-bold">
                    {formatDate(data.end)}
                  </div>
                </div>
              </div>
            </div>
          </div>

          {/* Bottom Decorative Border */}
          <div className="h-2 bg-gradient-to-r from-[#8c2e2e] via-[#c44545] to-[#8c2e2e]"></div>
        </div>
      </div>

      {/* Navigation Buttons */}
      <div className="absolute bottom-0 left-0">
        <PreviousButton onClick={prevComponent} />
      </div>
      <div className="absolute bottom-0 right-0">
        <button
          type="button"
          disabled={!isOwner}
          onClick={handleSubmit}
          className="inline-flex items-center justify-center gap-x-2 rounded-md bg-[#8c2e2e] px-4 py-3 text-sm font-semibold text-white shadow-lg shadow-[#8c2e2e]/20 hover:bg-[#722525] hover:shadow-md hover:shadow-[#c44545]/30 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-[#8c2e2e] transition-all duration-150 font-ui border-2 border-[#8c2e2e]"
        >
          <span className="text-white font-ui text-base leading-none flex items-center">
            ▶
          </span>
          <span className="transform translate-y-0.5 font-ui">
            Submit
          </span>
          <div className="flex space-x-1 transform translate-y-0.5">
            <div className="w-2 h-2 bg-cyan-400 animate-ping"></div>
            <div
              className="w-2 h-2 bg-cyan-400 animate-ping"
              style={{ animationDelay: "0.2s" }}
            ></div>
            <div
              className="w-2 h-2 bg-cyan-400 animate-ping"
              style={{ animationDelay: "0.4s" }}
            ></div>
          </div>
        </button>
      </div>
    </div>
  );
}
