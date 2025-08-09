export default function PreviousButton({onClick}) {
  return (
    <>
      <button
        type="button"
        onClick={onClick}
        className="inline-flex items-center justify-center gap-x-2 rounded-md bg-[#8c2e2e] px-4 py-3 text-sm font-semibold text-white shadow-lg shadow-[#8c2e2e]/20 hover:bg-[#722525] hover:shadow-md hover:shadow-[#c44545]/30 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-[#8c2e2e] transition-all duration-150 minecraft-font border-2 border-[#8c2e2e]"
        data-testid="previousbutton"
      >
        <span className="text-white minecraft-font text-sm leading-none transform -translate-y-0.5">◀</span>
        <span className="minecraft-font">Previous</span>
      </button>
    </>
  )
}