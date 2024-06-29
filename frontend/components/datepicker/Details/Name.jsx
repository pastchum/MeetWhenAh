export default function Name({handleInputChange}) {
    return (
      <div className="">
        <label htmlFor="event_name" className="block text-sm font-medium leading-6 text-gray-900">
          Event Name
        </label>
        <div className="mt-2">
          <input
            type="text"
            name="Event Name"
            id="event_name"
            onChange={handleInputChange}
            className="block w-full rounded-md border-0 py-1.5 text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 placeholder:text-gray-400 placeholder:pl-2 focus:ring-2 focus:ring-inset focus:ring-indigo-600 sm:text-sm sm:leading-6"
            placeholder="Name of your event!"
          />
        </div>
      </div>
    )
  }