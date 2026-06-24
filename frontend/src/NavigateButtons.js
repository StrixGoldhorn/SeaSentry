import { useNavigate } from "react-router";

export default function NavigateToInputsButton() {
  const navigate = useNavigate();

  return (
    <button
      onClick={() => navigate("/inputs")}
      style={{
        position: "absolute",
        top: "20px",
        right: "20px",
        zIndex: 1000,
        padding: "10px 15px",
      }}
    >
      Go To Inputs
    </button>
  );
}