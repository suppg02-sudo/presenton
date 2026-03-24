const layoutId = "blank";
const layoutName = "Blank";
const layoutDescription = "A completely blank slide for custom content";

const Schema = z.object({
  content: z.string().default("")
});

const dynamicSlideLayout = ({ data }) => {
  const containerStyle = {
    width: '100%',
    height: '100vh',
    backgroundColor: '#FFFFFF',
    display: 'flex',
    flexDirection: 'column',
    borderTop: '4px solid #8F1A95',
    boxSizing: 'border-box',
  };

  const contentStyle = {
    width: '100%',
    height: '100%',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    padding: '40px',
    boxSizing: 'border-box',
  };

  const placeholderStyle = {
    color: '#44546A',
    fontSize: '18px',
    fontFamily: 'Calibri, sans-serif',
    textAlign: 'center',
  };

  return (
    <div style={containerStyle} data-layout="blank">
      <div style={contentStyle}>
        <p style={placeholderStyle}>[Blank slide - add your content here]</p>
      </div>
    </div>
  );
};

